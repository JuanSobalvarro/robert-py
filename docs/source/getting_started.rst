Getting Started
===============

Installation
------------
To install RobeRT-py, run the following command:

.. code-block:: bash

   pip install robert-py

.. note::
   RobeRT-py requires Python 3.14 or higher.

Basic Usage
-----------
RobeRT works with a client-server architecture. You must first log in using the credentials provided by the administrator who set up the middleware server (see `robert-middleware` for more details).

After logging in, you must acquire a hardware lock using the ``client.acquire()`` method before the robot will accept your commands.

How does that look in code?
---------------------------

First, import the package:

.. code-block:: python

   import robert as rb

We highly recommend using a ``with`` statement (context manager) to initialize the ``RobeRTClient``. This ensures that your session is automatically logged out and the hardware lock is safely released when your script finishes or crashes:

.. code-block:: python

   with rb.RobeRTClient("server_ip", 42069) as client:
       client.login("username", "password")
       client.acquire()
       # Robot is now ready for commands!

Executing Commands
------------------
Some commands execute instantly (like ping), while physical movements take time. For movements, you could use ``wait_for_task_completion()`` to ensure the robot finishes its current action before sending the next one. It is not necessary to wait, specially if you are looking for real time interactions.

**Full Example:**

.. code-block:: python

   import robert as rb

   with rb.RobeRTClient("server_ip", 42069) as client:
       client.login("username", "password")
       client.acquire()

       response = client.ping()
       print(f"Ping response: {response}")

       response = client.get_status()
       response = client.wait_for_task_completion(response.task_id)
       print(f"Current status: {response.robot_status}")

       client.set_speed(100)

       print("Moving using offsets...")
       move_response = client.move_j_offs(x=10, y=0, z=0)
       client.wait_for_task_completion(move_response.task_id)

       print("Returning to zero...")
       zero_response = client.move_zero()
       client.wait_for_task_completion(zero_response.task_id)

       print("Context manager will now safely release and logout.")
