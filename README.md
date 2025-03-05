# ONTU Schedule Bot Admin

This project is the Backend for the ONTU Schedule Bot.
In this service you can:
- Add new users;
- Fetch faculties, groups, teachers and schedule;
- Create and send messages to users;
- Manage subscriptions of users;

## Installation

For local development - use Devcontainers, or follow the generic installation procedure.

To use this repository you need:
1. Install PDM package manager;
2. Install packages via PDM (`pdm install`);
3. Create `.env` file in the root of the project and fill it with the necessary environment variables;
4. Run the service via PDM (`pdm run start`).

## Environment

The `.env` file should contain the following:
```env
SECRET_KEY=your_secret_key
```
The secret key is used by Django Admin.

## Usage

### API

After launching this service you should have a running API on port 8000.
Opening `http://localhost:8000/` should bring you to a simple HTML page with a few buttons:
- To admin page;
- To API documentation;
- To Telegram Bot;

### Admin

You need to create a superuser to access the admin page.
To do this, run the following command:
```bash
pdm manage createsuperuser
```
Then, fill in the necessary fields.

There you will find three major sections:
- Admin Site Database;
- Admin Site Endpoints;
- Authentication and Authorization.

First is responsible for storing and fetching main entities of the application:
- Departments; (Used for Teachers)
- Faculties; (Used for Stutends)
- Groups; (Used for Students)
- Message campaigns; (Used for sending messages to users)
- Subscriptions; (Shows subscriptions of a Chats to a Group or a Teacher)
- Teacher schedule caches; (Used for caching schedules of teachers (weird placement, should be changed))
- Teachers;
- Telegram chats; (Used for storing Telegram chat IDs of users, and later - linking them to Subscriptions)

#### Loading in data

Run:
```bash
pdm manage load_departments
pdm manage load_teachers

pdm manage load_faculties
pdm manage load_groups
```

The order of departments and teachers is important, as teachers are linked to departments.
Same goes to faculties and groups.

Otherwise - run whatever you need.

You also can update faculties and groups from Admin by running action on a queryset.

### API

API is primarely used by the Telegram Bot, and is not ready (right now) to be used by anything else.
In general - API Requires a rewrite with DRF, as it is currently using Django Views.
