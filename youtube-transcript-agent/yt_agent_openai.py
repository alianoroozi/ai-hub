import re
import asyncio

from agents import Agent, function_tool, Runner
from openai.types.responses import ResponseTextDeltaEvent
from youtube_transcript_api import YouTubeTranscriptApi


def _extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid YouTube URL")
    return match.group(1)


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to [MM:SS] format."""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"[{minutes:02d}:{remaining_seconds:02d}]"


@function_tool
def fetch_youtube_transcript(url: str) -> str:
    """
    Fetch and format a YouTube video transcript.

    Args:
        url (str): YouTube video URL

    Returns:
        str: Transcript in the format "[MM:SS] text"
    """
    try:
        video_id = _extract_video_id(url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        formatted_transcript = [
            f"{_format_timestamp(segment['start'])} {segment['text']}"
            for segment in transcript
        ]
        return "\n".join(formatted_transcript)

    except Exception as e:
        raise RuntimeError(f"Error fetching transcript: {str(e)}")


async def main():
    agent = Agent(
        name="YouTube Transcript Agent",
        instructions="You are a helpful assistant providing help with YouTube videos.",
        tools=[fetch_youtube_transcript],
    )

    print("YouTube Transcript Agent")
    print("Type 'exit' to end the conversation")

    conversation_history = []

    while True:
        user_message = input("\nUser: ").strip()

        if not user_message:
            continue

        if user_message.lower() == "exit":
            print("\nGoodbye!")
            break

        conversation_history.append({"role": "user", "content": user_message})
        print("\nAgent: ", end="", flush=True)

        result = Runner.run_streamed(agent, input=conversation_history)

        async for event in result.stream_events():
            # We'll ignore the raw responses event deltas
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                print(event.data.delta, end="", flush=True)
            elif event.type == "agent_updated_stream_event":
                continue
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    print("\n-- Fetching transcript...")
                elif event.item.type == "tool_call_output_item":
                    conversation_history.append(
                        {
                            "content": f"Transcript:\n{event.item.output}",
                            "role": "system",
                        }
                    )
                    print("-- Transcript fetched.")
                elif event.item.type == "message_output_item":
                    conversation_history.append(
                        {"content": f"{event.item.raw_item}", "role": "assistant"}
                    )
                else:
                    pass  # Ignore other event types

        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
