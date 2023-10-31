# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Before Anything

Run `npm i` to install node packages.
Create a .env file in the root frontend directory; define your API URL in the .env file as seen below:
`REACT_APP_API_URL=http://127.0.0.1:8000`

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `docker compose -f docker-compose.development.yaml up --build`

To run the docker container instead of using npm; it will build the container first, the run it.
After the first build you can just run `docker compose -f docker-compose.development.yaml up`

### Deployment
#### Docker

To Deploy frontend I am making use of Docker.
```bash
docker build -t thefirsthero/confessions-react-frontend:{{tagname}} .
docker push thefirsthero/confessions-react-frontend:{{tagname}}
```

#### Firebase Hosting
1. Make sure firebase tools is installed: `npm install -g firebase tools`.
2. Login to firebase: `firebase login`.
3. Navigate to root project directory!
4. Initialise the firebase project: `firebase init`.
5. Choose Hosting, the Project, `build` as the public directory, and don't configure as a single-page app.
6. Run `npm run build` to build react app.
7. Run `firebase deploy` to deploy. 

NB: Consult the pdf guide in the `firebase_tutorial` directory for injecting environment variables into a firebase hosted react app.

### Docker Tutorial Videos that aided in this Project:

Found in`./docker_tutorial`