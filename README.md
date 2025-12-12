# UTOPIA: Multi-Agent Air-Ground Cooperative System

**Status:** Completed (Master's Thesis)  
**Tech Stack:** ROS, Gazebo, MATLAB, Python, C++

## 📖 Project Overview
The UTOPIA project focuses on the collaboration between an **Unmanned Aerial Vehicle (UAV)** and an **Unmanned Ground Vehicle (UGV)** to enhance navigation in unstructured environments. By utilizing an aerial perspective, the system improves the localization and path planning capabilities of the ground agent.

## ⚙️ Key Technical Contributions
* **Heterogeneous Sensor Fusion:** Implemented an **Extended Kalman Filter (EKF)** to fuse GPS, IMU, and visual odometry data from both agents.
* **Simulation Environment:** Developed a full-physics simulation in **Gazebo** to test multi-agent coordination protocols.
* **Hardware-in-the-Loop (HITL):** Validated algorithms using custom-built drone frames and rover platforms.

## 📊 Results
Based on the simulation tests, the algorithms are improved and modified for experimental work. It is observed that IMU alone, and IMU with Pose data, do not provide reasonable results. Visual odometry performs better indoors but worsens outdoors. Therefore, integrating IMU with visual odometry performs better. Outdoor localization is more challenging, and GPS has a correcting impact on localization.

The results reveal that incorporating more sensor data into the EKF reduces the RMSE, thereby improving localization. In homogeneous mobile robot systems, where each robot has similar sensors, localization can be achieved with a comparable RMSE. However, in heterogeneous systems, the higher variances in sensor capabilities and performance need careful management to ensure robust localization for cooperative tasks.

For example, UAVs move faster and have a larger field of vision, but they have limited load capacity and battery life. In contrast, UGVs move slower but can carry more load and have longer battery life. These differences highlight the need for a robust localization system for effective task coordination.

One issue observed during experimental tests was time synchronization between the robots. In homogeneous mobile robot systems, this can be tolerated because each robot has similar components and similar moving capacity. However, in heterogeneous systems, it clearly affects task performance. For example, late messages and unmatched time steps during QR scanning led to incorrect estimations of the UGV's position in cooperative mission 2. To address this, we installed the "chrony sync time" package for Ubuntu and configured the ROS environment to eliminate time synchronization problems.

Another problem identified during the tests was the high computational costs and delayed messages due to outdoor wireless communication. The diversity of sensors and large amounts of high-frequency data caused the controller boards to work much slower in outdoor tests, leading to localization issues. We mitigated this by setting the robots to work headless, reducing GPU use, and optimizing each robot’s EKF nodes to run on the robot’s controller board. We also canceled the cameras' raw topics and unnecessary image topics, narrowed the camera's scope during image processing, and isolated each sensor from magnetic effects.

In conclusion, this research underscores the importance of integrating diverse sensor data to improve localization accuracy in heterogeneous robotic systems. The insights gained contribute to the development of robust cooperative localization and control strategies, enhancing the capabilities of mobile robots in complex environments. Future work should aim to refine these strategies further to improve the performance and reliability of diverse robotic systems in different applications.
## 📂 Repository Structure
* `/simulation`: Gazebo world files and launch scripts.
* `/algorithms`: Python/C++ implementations of the EKF and coordination logic.
* `/docs`: System architecture diagrams and thesis summary, published papers.
