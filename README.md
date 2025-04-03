# Team Deadlock
**Copy** of the repository for the team Deadlock for Newsmatics Hackathon 2025
- Team captain: Erik Čapkovič
- Authors: Erik Čapkovič, Lukáš Denkócy, Rastistlav Kollár, Lukáš Medovič, Peter Štefunko

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- [Python 3.13+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [PostgreSQL](https://www.postgresql.org/download/)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/peter-stefunko/team-deadlock
    cd team-deadlock
    ```

2. Install the dependencies using Poetry:

    ```sh
    cd backend
    poetry install
    ```

3. Set up the environment variables:

    Create a `.env` file in the root of the project and add the necessary environment variables. Refer to `.env.template` for the required variables.

## Python venv

1. To develop in terminal, run the following command in the `backend` directory:
   ```sh
   source $(poetry env info --path)/bin/activate
   ```
2. If you are using an IDE for development like PyCharm or VSCode, refer to their own guide for setting up a Poetry environment.

## Database Migration

1. To create a new migration, use:

    ```sh
    alembic revision
    ```

## Running the Project

1.Firstly, you should build the whole project with:
    ```sh
    make build
    ```

2. You should now be able to start it up with:

    ```sh
    make start
    ```

3. The backend should now be running at `http://localhost:8000`. (with the swagger being at `http://localhost:8000/api/docs`)
   
   ![image](https://github.com/user-attachments/assets/c3af91b8-a4ad-4e73-9ccd-346c918a8a1d)

5. You should be able to access the website at `http://localhost`.
   
![CleanShot 2025-03-01 at 14 57 13@2x](https://github.com/user-attachments/assets/3d7982ba-e354-41d2-a550-f3be9d9e59f8)


5. For more `make` commands, run the following:
   ```sh
   make help
   ```
## Usage
- Once you have it up and running, you can now use it to it's fullest potentiol. On the main screen of the website, there is a user search input where you can ask our system anything in you owns words, and it should find the most accurate article you are looking for.
- You can also use the random phrase generator on the left, if you feel lucky
- There are also filters on the left, and bellow the search bar, you can toggle addiotional categories, which are appended to your's search input for further enhancing similarity accuracy
- Every article is composed of the clickable title, trust score from 0 to 5, publisher, classification and also you can click up or downvote to change the article's trust score

   
## Live Demo

We have a live demo of the project where you can explore the embedding-based search functionality in action.

- **Demo URL:** [Live Demo](http://193.187.129.146)
- **Demo Swagger:** [Live Swagger](http://193.187.129.146:8000/api/docs)
- **Usage:** Simply enter your query in the search bar, and our backend will retrieve the most relevant results using our optimized embedding-based search.
- **Authentication:** Some features may require authentication. If applicable, refer to the provided test credentials or register for access.
- **Feedback:** If you encounter any issues or have suggestions, please open an issue in this repository or contact us.

Check out the demo and experience our solution firsthand!


