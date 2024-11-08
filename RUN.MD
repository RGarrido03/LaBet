# Instructions to run the project

## 1. Clone the repository

## 2. Install the dependencies

## 3. Run the project

## 4. Visit localhost:8000 in your browser

## 5. Enjoy the application

## Commands

1.

```bash
git clone git@github.com:RGarrido03/LaBet.git # please HTTPS it's a shit
cd LaBet
```

2.

```bash
python3 -m venv venv
source venv/bin/activate # IN UNIX BASED, in windows i don't care about it
pip install -r requirements.txt
```

3.

```bash
python manage.py migrate
python manage.py qcluster
# and in another shell
python manage.py runserver
```

4.

Visit localhost:8000 and use the app

