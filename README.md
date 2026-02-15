# 📰 Newsletter Bot 🤖

A Python application that fetches news articles from GNews, generates engaging newsletter content using OpenAI, and saves the generated content to a text file. It's designed to automate the process of creating newsletters, saving time and effort. The project leverages Langchain for agent management and Pydantic for data validation, ensuring a robust and maintainable solution. It also has commented-out Kafka integration, suggesting future capabilities for distributing newsletters via a message queue.

## 🚀 Key Features

- **Automated News Fetching:** Fetches the latest news articles from the GNews API using the `GNewsService`.
- **AI-Powered Content Generation:** Generates newsletter content using OpenAI's language models, driven by the `NewsLetterBot`.
- **Structured Data Modeling:** Uses Pydantic models (`NewsletterArticleModel`, `TopicModel`, `SourceModel`) to ensure data consistency and validity.
- **Agent-Based Architecture:** Employs Langchain agents for specific tasks like JSON parsing, managed by the `MultiAgents` class.
- **Text File Output:** Saves the generated newsletter content to a `.txt` file using the `save_newsletter_to_txt` utility.
- **Redis Cache:** Caches already published newsletters to avoid re-processing.
- **Kafka Integration:** Sends newsletters to a Kafka topic for downstream processing.
- **Dockerized Deployment:** Provides a `docker-compose.yml` file for easy setup of Redis, Kafka, Zookeeper, and Kafdrop.

## 🛠️ Tech Stack

- **Backend:** Python
- **AI Tools:** OpenAI, Langchain
- **Data Validation:** Pydantic
- **API Interaction:** `requests`
- **Kafka Integration:** `confluent-kafka`
- **Environment Management:** `dotenv`
- **Build Tool:** Poetry
- **Containerization:** Docker, Docker Compose

| Category             | Technology             | Version          |
| -------------------- | ---------------------- | ---------------- |
| Programming Language | Python                 | >=3.13,<4.0      |
| AI Framework         | Langchain              | >=0.3.27,<0.4.0  |
| OpenAI Integration   | langchain-openai       | >=0.3.32,<0.4.0  |
| OpenAI Library       | openai                 | >=1.102.0,<2.0.0 |
| Data Validation      | Pydantic               | N/A              |
| HTTP Client          | requests               | N/A              |
| Kafka Client         | confluent-kafka        | >=2.11.1,<3.0.0  |
| Env Variables        | dotenv                 | >=0.9.9,<0.10.0  |
| Build System         | Poetry                 | N/A              |
| Containerization     | Docker, Docker Compose | N/A              |
| Langchain Community  | langchain-community    | >=0.3.29,<0.4.0  |

## 📦 Getting Started

### Prerequisites

- Python (>=3.13,<4.0)
- Poetry
- Docker (optional, for Kafka/Redis setup)
- OpenAI API key
- GNews API key

### Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  Install dependencies using Poetry:

    ```bash
    poetry install
    ```

3.  Create a `.env` file in the root directory and add your API keys:

    ```
    OPENAI_API_KEY=<your_openai_api_key>
    GNEWS_API_KEY=<your_gnews_api_key>
    REDIS_URL=redis://localhost:6379/0
    CACHE_TTL_SECONDS=1200
    ```

### Running Locally

1.  Activate the Poetry shell:

    ```bash
    poetry shell
    ```

2.  Run the main script:

    ```bash
    python main.py
    ```

    This will start the process of fetching news, generating newsletters, and saving them to the `newsletters` folder.

3.  (Optional) Start Kafka/Redis using Docker Compose:

    ```bash
    docker-compose up -d
    ```

    This will start Redis, Zookeeper, Kafka, and Kafdrop. You can access Kafdrop at `http://localhost:19000` to monitor the Kafka cluster.

## 📂 Project Structure

```
├── main.py
├── modules
│   ├── agents_service.py
│   ├── gnews_service.py
│   ├── kafka_newsletter_producer.py
│   └── openai_service.py
├── models
│   ├── newsletter_bot_json_article.py
│   ├── source_model.py
│   └── topic_model.py
├── utils
│   └── to_txt.py
├── pyproject.toml
├── README.md
└── docker-compose.yml
```

## Examples

You can see all news in the newslletters path

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with descriptive messages.
4.  Submit a pull request.

## 📝 License

This project is licensed under the [MIT License](LICENSE).

## 📬 Contact

If you have any questions or suggestions, feel free to contact me at [your_email@example.com](mailto:your_email@example.com).

## 💖 Thanks Message

Thank you for checking out the Newsletter Bot project! I hope it's helpful for automating your newsletter creation process. Your feedback and contributions are highly appreciated!

This README is written by [readme.ai](https://readme-generator-phi.vercel.app/).
