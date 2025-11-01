import simpy
import random
import statistics
import matplotlib.pyplot as plt

# =====================
# PARAMETERS
# =====================
SIM_TIME = 480  # Simulation time in minutes (8 hours)
INTER_ARRIVAL_MEAN = 5  # Average time between calls

# Scenario settings: (num_agents, service_time_mean)
SCENARIOS = {
    "Scenario A (3 agents, 10 min avg service)": (3, 10),
    "Scenario B (5 agents, 10 min avg service)": (5, 10),
    "Scenario C (3 agents, 7 min avg service)": (3, 7)
}

# =====================
# FUNCTIONS
# =====================
def customer(env, name, agents, service_mean, wait_times, queue_lengths, service_times):
    arrival_time = env.now
    
    # Record current queue length
    queue_lengths.append(len(agents.queue))
    
    with agents.request() as request:
        yield request
        wait = env.now - arrival_time
        wait_times.append(wait)
        
        # Generate service time and track it
        service_time = random.expovariate(1 / service_mean)
        service_times.append(service_time)
        
        yield env.timeout(service_time)

def setup(env, num_agents, service_mean, wait_times, queue_lengths, service_times):
    agents = simpy.Resource(env, capacity=num_agents)
    i = 0
    while True:
        yield env.timeout(random.expovariate(1 / INTER_ARRIVAL_MEAN))
        i += 1
        env.process(customer(env, f"Call {i}", agents, service_mean, wait_times, queue_lengths, service_times))

# =====================
# RUN SIMULATION FOR EACH SCENARIO
# =====================
results = {}

for scenario_name, (num_agents, service_mean) in SCENARIOS.items():
    env = simpy.Environment()
    wait_times = []
    queue_lengths = []
    service_times = []
    
    env.process(setup(env, num_agents, service_mean, wait_times, queue_lengths, service_times))
    env.run(until=SIM_TIME)
    
    avg_wait = statistics.mean(wait_times) if wait_times else 0
    max_queue = max(queue_lengths) if queue_lengths else 0
    agent_utilization = (sum(service_times) / (num_agents * SIM_TIME)) * 100 if service_times else 0
    
    results[scenario_name] = {
        "Average Wait Time": avg_wait,
        "Max Queue Length": max_queue,
        "Agent Utilization (%)": agent_utilization,
        "All Wait Times": wait_times
    }

# =====================
# PRINT RESULTS
# =====================
for scenario, metrics in results.items():
    print(f"\n{scenario}")
    print(f"Average Wait Time: {metrics['Average Wait Time']:.2f}")
    print(f"Max Queue Length: {metrics['Max Queue Length']:.2f}")
    print(f"Agent Utilization (%): {metrics['Agent Utilization (%)']:.2f}")

# =====================
# VISUALIZATIONS
# =====================
# 1. Average Wait Time Comparison
plt.figure(figsize=(8,5))
avg_waits = [metrics["Average Wait Time"] for metrics in results.values()]
plt.bar(results.keys(), avg_waits, color='skyblue', edgecolor='black')
plt.ylabel("Average Wait Time (minutes)")
plt.title("Average Wait Time Across Scenarios")
plt.xticks(rotation=15)
plt.show()

# 2. Max Queue Length Comparison
plt.figure(figsize=(8,5))
max_queues = [metrics["Max Queue Length"] for metrics in results.values()]
plt.bar(results.keys(), max_queues, color='salmon', edgecolor='black')
plt.ylabel("Max Queue Length")
plt.title("Maximum Queue Length Across Scenarios")
plt.xticks(rotation=15)
plt.show()

# 3. Histogram of Wait Times for Scenario A
plt.figure(figsize=(8,5))
plt.hist(results["Scenario A (3 agents, 10 min avg service)"]["All Wait Times"], bins=20, color='lightgreen', edgecolor='black')
plt.xlabel("Wait Time (minutes)")
plt.ylabel("Number of Calls")
plt.title("Distribution of Wait Times - Scenario A")
plt.show()
