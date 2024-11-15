# :art: SmartArters

SmartArters is a web application designed to help users rank and manage artworks for the Altera Trondheim Art Club. 
It provides a platform for users to log in, view, and rank artworks, as well as mark them as won.

## :hammer: Prerequisites 

- Docker
- SMTP server
- Reverse proxy (Recommended)

## :whale: Running with Docker Compose

To run the application using Docker Compose, follow these steps:

1. Create a `docker-compose.yml` file:

    ```yaml
    services:
        smartarts:
            image: ghcr.io/ksolheim/smartarters:latest
            container_name: smartarters-container
            ports:
            - "6001:6001"
            volumes:
            - smartarters_db:/app/database
            env_file:
            - .env
            restart: unless-stopped

    volumes:
        smartarters_db:
            name: smartarters_db
    ```

2. Create a `.env` file in the root directory with the necessary environment variables. You can use the `.env.example` as a template.

3. Start the application:

   ```bash
   docker compose up -d
   ```

   This command will pull and start the application in detached mode. The application will be accessible at `http://localhost:6001`.

4. To stop the application, run:

   ```bash
   docker compose down
   ```
    It is recommended to use a reverse proxy to serve the application, such as Nginx.

## :construction: Setting Up a Development Environment

To set up a development environment, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/ksolheim/smartarters.git
   cd smartarters
   ```

2. Create a `.env` file in the root directory with the necessary environment variables. You can use the `.env.example` as a template.

3. Build the Docker image manually:

   ```bash
   docker build -t smartarters:dev .
   ```

   This command will build the Docker image using the `Dockerfile`.

4. Run the Docker container:

   ```bash
   docker volume create smartarters_db
   docker run -v smartarters_db:/app/database --name smartarters-dev -p 6001:6001 --env-file .env smartarters:dev
   ```

   This command will start the application in a Docker container. The application will be accessible at `http://localhost:6001`.

5. To stop the container, run:

   ```bash
   docker stop smartarters-dev
   ```

6. To remove the container, run:

   ```bash
   docker rm smartarters-dev
   ```

## :page_facing_up: License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
