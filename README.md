# DropMe API Project

## Getting started

### Prerequisites

1. Download [Python](https://www.python.org/downloads/)

2. Clone Repo
    ```shell
    git clone https://github.com/ahmedsaeed102/dropme.git
    ```

3. Go to dropme folder
    ```shell
    cd dropme
    ```

4. Create virtual environment
    ```shell
    python -m venv venv
    ```

5. Activate virtual enviroment
    ```shell
    venv/bin/activate
    or
    ./venv/scripts/activate.ps1
    ```

6. Install requirements
    ```shell
    pip install -r requirements.txt
    ```

7. Install [GeoDjango](https://docs.djangoproject.com/en/4.1/ref/contrib/gis/install/)

8. connect to local database and migrate to database
    ```shell
    python manage.py migrate
    ```

9. Start development server
    ```shell
    python manage.py runserver
    ```