# Event Management System Backend

## Overview
This is the backend for the Event Management System, allowing users to authenticate, create and participate in events, manage profiles, and track attendance. It is built using FastAPI and follows a JWT-based authentication system.

## Project Documentations

- **Backend_Best_practices**: (https://docs.google.com/document/d/1lH9lpqAo3dPOHVDWarAZ8ArCdsjF1OBbJeTrfmNrK28/edit?usp=sharing)
- **Database Table Link**: (https://docs.google.com/document/d/1dxaPvoU5PXwQuVd9brAtNH7yDkBrofcMPJ5gEAPDTvc/edit?usp=sharing).
- **API Documentation Link**: (https://www.notion.so/API-DOCUMENTATION-1b2ed91fd20480e8b497c151af31f922?pvs=4).

## Features
- **User Authentication**: JWT and cookies-based authentication system.
- **Event Management**:
  - Users can create events.
  - Users can view events they registered in.
  - Users can view the events they created.
- **Profile Management**:
  - Users can see and update their profiles.
- **Participant Management**:
  - Event creators can view participant details.
  - Event creators can manage participant attendance.
- **Cloudinary Integration**:
  - Used to store event images and profile images.
- **Geoapify Integration**:
  - Used to get coordinates of the given address.

## Tech Stack
- **FastAPI**: Web framework for building APIs.
- **JWT (JSON Web Tokens)**: Used for authentication.
- **Cloudinary**: Image storage for events and profiles.
- **Geoapify**: Retrieves coordinates based on addresses.
- **SQLAlchemy**: ORM for database management.
- **MySQL**: Database system.


## Tools 
- **Ruff**: Used for formatting and linting python code.

