# Blockchain-Contact-Tracing

This repository is cresponding to the paper "Blockchain Driven Privacy Preserving Contact Tracing Framework in Pandemics".
Arxiv link: https://arxiv.org/abs/2202.09407 

### Introduction
Contact tracing has been proven an effective approach to control the virus spread in pandemics like COVID-19 pandemic. As an emerging powerful decentralized technique, blockchain has been explored to ensure data privacy and security in contact tracing processes. However, existing works are mostly high-level designs missing crucial design details or sufficient demonstration on effectiveness and treat blockchain as separate storage system assisting third-party central servers, ignoring the importance and capability of consensus mechanism and incentive mechanism. In this paper, we propose a light-weight and fully third-party free **B**lockchain-**D**riven **C**ontact **T**racing framework (BDCT) to bridge the gap. In the BDCT framework, RSA encryption based transaction verification method (RSA-TVM) is proposed to ensure contact tracing correctness, which can achieve more than 96\% contact cases recording accuracy even each person has 60\% probability of failing to verify the contact information. Reputation Corrected Delegated Proof of Stake (RC-DPoS) consensus mechanism is proposed together with the incentive mechanism, which can ensure timeliness of reporting contact cases and keep blockchain decentralized. A novel contact tracing simulation environment is created, which considers three different contact scenarios based on population density. The simulation results and discussion demonstrate the effectiveness, robustness  of RSA-TVM and RC-DPoS and low storage cost of proposed BDCT.

### Results

#### Dicentrality Comparision
BDCT:
[new600diff_user_5_ban_reward_non_restricted_10000.pdf](https://github.com/Gyou/Blockchain-Contact-Tracing/files/10187646/new600diff_user_5_ban_reward_non_restricted_10000.pdf)
DPoS:
[new600diff_user_5_ban_reward_non_restricted_BenchMark_10000.pdf](https://github.com/Gyou/Blockchain-Contact-Tracing/files/10187654/new600diff_user_5_ban_reward_non_restricted_BenchMark_10000.pdf)

#### Robustness Demonstration
![image](https://user-images.githubusercontent.com/8926142/206515334-cb6fe939-21d7-4e13-bcbc-a96cdd178be0.png)
