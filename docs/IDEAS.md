## **My first impression:**
There are 4 columns when we talk about delivery, 4 constraints that should be considered: weight, temp. sensitivity, urgency and location.

1. sort the temperature sensitive ones into the relevant truck.

2. Now urgent deliveries based on their weight

3. Then the rest of the deliveries based on distance

**Here's the initial understanding of the project:**

in the morning, the drivers pick up the deliveries from one inventory. there are 5 drivers, 6 vans. 3 small vans, 2 big ones and 1 refrigrated one
distant deliveries should go with bigger vans and near ones with the smaller vans. some deliveries are temp sensitive and must go with the refrigrated truck, and there are 3 destinations: hospitals, clinics and pharmacies. hospitals and clinics are more urgent but all deliveries should be done within 24 hours.
I know I should use google maps API for locations and traffic
And I have this idea of using toplogical sort for the deliveries that the driver sees

But i don't know how to take into account all constraints at the same time while choosing the right tools for our flask app
there should be a dashboard for management, an authentication page and a drivers page