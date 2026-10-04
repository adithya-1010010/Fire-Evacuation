# Intelligent Fire Evacuation Agent

A small Fundamental AI project. A person (the **agent**) is inside a building and fire appears
over time. The agent must reach the exit. It uses **classical AI only**: rule-based reasoning,
A* search with the Manhattan heuristic, a simple memory of seen fire, and replanning.

No machine learning. The core and the terminal version need no packages. An optional
Pygame window draws the same simulation, and an optional Streamlit page serves it in a browser.

## Run

Python 3.8 or newer.

Terminal version (nothing to install):

    python run.py

Pygame window (needs `pip install pygame`):

    python main.py

Run the tests:

    python -m unittest discover tests

## Web version (free hosting from this GitHub repository)

`streamlit_app.py` runs the same simulation in a browser: pick an environment, then step
through it or run it to the end.

Locally:

    pip install -r requirements.txt
    streamlit run streamlit_app.py

Free on the internet, hosted by Streamlit (no server of your own, no Procfile):

1. Push this repository to GitHub.
2. Go to <https://share.streamlit.io> -> **Deploy** -> **Yes, get started**.
3. Connect the GitHub repository, pick the branch, and press **Deploy**.
4. Streamlit builds `requirements.txt`, starts `streamlit_app.py`, and gives you a
   `https://<your-name>.streamlit.app` address. Every push to that branch redeploys it.

GitHub Pages cannot run this project: it only serves static files, and a Pygame window needs a
real desktop. Streamlit Community Cloud is the free option that serves Python from the repository.

## Menu

    1. New Simulation   -> Random Environment | Custom Environment (rows, columns, difficulty)
    2. Preset Scenarios -> Fire Blocks Route | Multiple Replanning | No Safe Route
    3. Help
    4. Exit
