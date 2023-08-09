# Drop Me API Project

## Quick Start

1. Download [Python](https://www.python.org/downloads/). Minimum version 3.10

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

6. Install dev requirements
    ```shell
    pip install -r requirements_dev.txt
    ```

7. Install [GeoDjango](https://docs.djangoproject.com/en/4.1/ref/contrib/gis/install/)

8. Connect to local database and create `.env.local` file with your database credentials using following env variables: `local_db_host`, `local_db_name`, `local_db_user`, `local_db_password`, `local_db_port`.  

9. Start development server
    ```shell
    python manage.py runserver
    ```