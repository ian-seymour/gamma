In current state, this has barebones functionality but can create accounts, login/logout, and do basic weather queries based on city (uses openmaps to convert city names
into lat long coords for NOAA's api, as well as ensure location validation). Weather returns correct forecasts (but a little less verbose than you might see on other sites).

Most of the functions we needed could be handeled almost entirely through Python libraries or Flask specific libraries or modules. Forms makes handling user input for
account creation super easy. Out of the box password hashing/hash checking is used and it works great, several other security libraries are also included. There's
even a library being used that does a basic validation check on emails (even better than checking for an "@").

To run, be sure to install uv (a Python package manager) on your machine and create an environment in the route directory and feed it "requirements.txt", if you clone
the repo as is, simply installing uv and sourcing the .venv folder's source file might be enough.

Once UV is figured out, go to the root of Gamma folder and type: flask run --debug

It will start a server with and list an http:// with an ip adress and a port, copy paste that in browser to view app. If you get module not found errors,
the issue is your UV install or you're not in its environment.

To do:
- Make UI actually look like intended design, right now it's barebones bootstrap with pure defaults.
- Get AirNow for air quality data setup.
- Integrate password security requirements.
- Using NOAA's api, it seems we cannot query locations outside the US. We may want to address this, but it might mean a second api...
