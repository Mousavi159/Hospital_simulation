import random  # For generating random numbers
import simpy  # For simulating events over time
import matplotlib.pyplot as plt  # For data visualization

# Setting up basic constants for the simulation:
RANDOM_SEED = 48  # Random seed for reproducibility
NUM_DOCTORS = 2  # Initial number of doctors
TREATMENT_TIME = 5  # Average treatment time for a patient (mean of exponential distribution)
T_INTER = 7  # Average time between patient arrivals (mean of exponential distribution)
SIM_TIME = 100  # Total simulation time
TREAT_PROBABILITY = 0.8  # Probability that a patient gets treated

# Lists to keep track of event timings:
arrival_times = []  # Times when patients arrive
treated_times = []  # Times when patients are treated
left_without_treatment_times = []  # Times when patients leave without treatment
wait_times = []  # Times patients spend waiting before being treated

# Define a Hospital class to handle hospital functions:
class Hospital(object):
    def __init__(self, env, num_doctors, treatment_time):
        self.env = env  # Current simulation environment
        self.doctor = simpy.Resource(env, num_doctors)  # Resource representing doctors
        self.treatment_time = treatment_time  # Average treatment time

    def treat(self, patient):
        # Simulate treatment of a patient with exponential distribution
        treatment_duration = random.expovariate(1 / self.treatment_time)
        yield self.env.timeout(treatment_duration)  # Wait for treatment to complete
        print(f"{patient} was treated in {treatment_duration:.2f} minutes.")  # Print message about treatment

# Function that simulates a patient's behavior in the hospital:
def patient(env, name, hospital):
    # Patient's arrival and arrival time are recorded
    print(f'{name} arrives at the hospital at {env.now:.2f}.')
    arrival_times.append(env.now)

    # Patient requests treatment
    with hospital.doctor.request() as request:
        yield request  # Wait until a doctor is available

        wait_time = env.now - arrival_times[-1]  # Calculate wait time for this patient
        wait_times.append(wait_time)  # Record the wait time

        # Decide if the patient gets treated or leaves
        if random.random() < TREAT_PROBABILITY:
            yield env.process(hospital.treat(name))  # Patient's treatment time is recorded
            print(f'{name} leaves the hospital after being treated at {env.now:.2f}.')
            treated_times.append(env.now)
        else:
            # Patient's departure time (without treatment) is recorded
            print(f'{name} chooses to leave the hospital without treatment at {env.now:.2f}.')
            left_without_treatment_times.append(env.now)

# Setting up the simulation: start with a few patients and add more over time
def setup(env, num_doctors, treatment_time, t_inter):
    hospital = Hospital(env, num_doctors, treatment_time)
    
    # Start with initial patients
    for i in range(1, 5):
        env.process(patient(env, f'Patient {i}', hospital))

    # Add new patients at random intervals
    i = 5
    while True:
        inter_arrival_time = random.expovariate(1 / t_inter)
        yield env.timeout(inter_arrival_time)
        print(f'Patient {i} arrives after {inter_arrival_time:.2f} minutes.')
        env.process(patient(env, f'Patient {i}', hospital))
        i += 1

# Function to add more doctors during the simulation
def add_doctors(env, hospital, num_doctors_to_add):
    print(f'Adding {num_doctors_to_add} new doctors at t = {env.now}.')
    
    # Increase doctor count (only informational, as `simpy.Resource` can't dynamically adjust size)
    for _ in range(num_doctors_to_add):
        hospital.doctor.request()
        yield env.timeout(0)

# Initialize and run the simulation:
print('Hospital Simulation (M/M/c Queue)')
random.seed(RANDOM_SEED)  # Set seed for reproducibility

# Create a new simpy environment
env = simpy.Environment()
hospital = Hospital(env, NUM_DOCTORS, TREATMENT_TIME)
env.process(setup(env, NUM_DOCTORS, TREATMENT_TIME, T_INTER))
env.run(until=SIM_TIME)  # Run the first part of the simulation

env.process(add_doctors(env, hospital, 2))
env.run(until=200)  # Run the second part of the simulation (after adding doctors)

# Create and display histograms with matplotlib:
time_points = sorted(set(arrival_times + treated_times + left_without_treatment_times))
cumulative_arrivals = [sum(1 for t in arrival_times if t <= time) for time in time_points]
cumulative_treated = [sum(1 for t in treated_times if t <= time) for time in time_points]
cumulative_left = [sum(1 for t in left_without_treatment_times if t <= time) for time in time_points]

# Plot cumulative counts as a line graph
plt.figure(figsize=(12, 8))
plt.plot(time_points, cumulative_arrivals, label='Cumulative Arrivals', color='blue', marker='o')
plt.plot(time_points, cumulative_treated, label='Cumulative Treated', color='green', marker='o')
plt.plot(time_points, cumulative_left, label='Cumulative Left Without Treatment', color='red', marker='o')

# Labeling the plot
plt.title('Hospital Simulation Results (Cumulative Over Time)')
plt.xlabel('Time (minutes)')
plt.ylabel('Cumulative Number of Patients')
plt.legend()
plt.grid(True)

# Show the line plot
plt.show()

# Calculate and print results
# Calculate and print results
total_patients = len(arrival_times)
treated_count = len(treated_times)
left_without_treatment_count = len(left_without_treatment_times)
average_wait_time = sum(wait_times) / len(wait_times) if wait_times else float('inf')

print("\n--------------------------------------------------------------")
print("Expected percentage of patients to be treated:", TREAT_PROBABILITY * 100, "%")
print("Total Patients:", total_patients)
print("Number of patients treated:", treated_count)
print("Number of patients who left without treatment:", left_without_treatment_count)
print(f"Actual percentage of treated patients: {(treated_count / total_patients) * 100:.2f}%")
print("Average wait time for treated patients: %.2f minutes" % average_wait_time)


# Display the histogram
#plt.show()