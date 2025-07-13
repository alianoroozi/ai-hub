# Chat Bot Feedback System

## Overview

This project is a simple chat bot application designed to collect user feedback, store it in a MongoDB collection, and process changes for integration into a larger reinforcement learning with human feedback (RLHF) system. A Change Data Capture (CDC) module monitors the MongoDB collection for feedback updates and publishes them to a RabbitMQ queue. A worker consumes these changes for further processing in a feature engineering pipeline.

## Components
- `src/bot/`: Contains chat bit and feedback collection modules.
- `src/db/`: Contains MongoDB connection.
- `src/data_cdc/`: Conains Change Data Capture (CDC) Module, which watches for changes in the MongoDB feedback collection and publishes them to a RabbitMQ queue.
- `src/mq/`: Contains RabbitMQ connection, publishing, and consuming modules.


# Purpose
This system is a component of a larger RLHF pipeline, where user feedback is processed and integrated into a dataset for reinforcement learning.
