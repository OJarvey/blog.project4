# Blog Soul

![Screenshot of the blog](readme_img/screenshot-2024-12-29.png)

A fully responsive blog website built with Django. This project supports user authentication, dynamic content, and searching with trigram similarity.

## Overview

This project is a blogging platform that enables users to create, edit, and delete blog posts. Visitors can view posts and search for specific content using an advanced trigram similarity algorithm.

## UX

This site was designed with the Five Planes of UX methodology.

### Strategy

**Goal:** Create an intuitive, responsive, and feature-rich blogging platform for users to share and discover content.

**Objectives:**

- Provide user-friendly interfaces for browsing and managing posts.
- Implement robust search functionality to improve content discovery.
- Ensure seamless mobile and desktop experiences.

### Scope

**User Features:**

- Responsive layout across devices.
- CRUD functionality for blog posts.
- Authentication and account management.

**Admin Features:**

- Manage user posts.
- View and delete inappropriate content.

### Structure

The website structure is designed to make navigation intuitive and efficient for users.

**Navigation:**

- Main Navigation: Includes links to Home, About, Login/Logout, and Create Post.

**Home Page:**

- Displays a list of blog posts with options to filter and search.
- Pagination for easier navigation through posts.

**Post Detail Page:**

- Shows the full content of a blog post.
- Includes comments section for user interaction.

**Admin Dashboard:**

- Admin-only view for managing posts and users.

**User Account Page:**

- Lists user-specific posts with options to edit or delete.

**Sitemap:**

- A visual sitemap was created to plan the site’s structure and navigation paths.

### Skeleton

**Wireframes:**

- Wireframes for both mobile and desktop versions were created using Balsamiq.

### Surface

**Color Scheme and Fonts:**

- Colors: Shades of brown, blue, orange, and gray for a professional look.
- Fonts: Google Fonts - Roboto for body text and Montserrat for headings.

**Visual Effects:**

- Smooth hover transitions on buttons and links.
- Dynamic animations for page transitions.

## Features

### Existing Features

- **Create, Read, Update, Delete Posts:** Users can manage their posts through an intuitive interface.
- **Advanced Search:** Trigram-based search for precise and fast content discovery.
- **User Authentication:** Secure registration and login system.
- **Responsive Design:** Optimized for all screen sizes using Materialize CSS.

### Potential Future Features

- Add a like and share functionality for posts.
- Enable user comments with moderation.
- Include categories and tags for better content organization.

## Responsive Layout and Design

The site was tested on multiple devices, ensuring consistency in layout and functionality across different screen sizes.

## Tools Used

**Development Tools:**

- Flask: Backend framework.
- SQLAlchemy: ORM for database operations.
- Materialize CSS: Frontend styling.
- Heroku: Deployment.

**Python packages:**

- Flask-WTF: For form validation.
- Flask-Login: User authentication.
- Psycopg2: PostgreSQL adapter.

## Testing

Extensive manual and automated testing was conducted for all features, ensuring robustness and usability.

## Bugs

- **Admin page errors:** Resolved by updating routing configurations.
- **Search delay:** Optimized by indexing the database.

## Deployment

### Setting up the Database

1. **Initialize and migrate the database using Flask-Migrate.**

### Heroku Deployment

1. **Create a Heroku app and connect the GitHub repository.**
2. **Add environment variables for database connection and secret keys.**

### Fork the Repository

Follow the GitHub fork instructions to create a personal copy of the repository.

### Clone the Repository

Use the git clone command to download the repository to your local machine.

## Credits

**Content:**

- All content was authored for this project.

**Media:**

- Images sourced from Unsplash.

**Code:**

- Flask documentation for route handling.
- Materialize CSS documentation for frontend components.

**Acknowledgements:**

- Special thanks to mentors and peers who provided valuable feedback and guidance during development.

Spencer Barriball
