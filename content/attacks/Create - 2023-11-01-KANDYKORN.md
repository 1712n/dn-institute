---
date: 2023-10-31
target-entities: macOS
entity-types:
   - Blockchain
   - Exchange
attack-types:
   - Race Condition Exploit
title: "North Korean Hackers Targeting Crypto Experts with KANDYKORN macOS Malware."
loss: No monetary loss
---

## Summary

State-sponsored [threat](https://thehackernews.com/2023/11/north-korean-hackers-tageting-crypto.html) actors from North Korea, specifically the Lazarus Group, have been identified targeting blockchain engineers on a crypto exchange platform through Discord using a new macOS malware called KANDYKORN. The attackers employed social engineering on a public [Discord](https://www.bitdegree.org/crypto/news/lazarus-group-targets-crypto-engineers-with-stealthy-macos-malware) server, impersonating blockchain engineers to trick victims into downloading and executing a ZIP archive containing malicious code. The malware, KANDYKORN, is a sophisticated implant with capabilities such as monitoring, interacting, and evading [detection.](https://thehackernews.com/2023/11/north-korean-hackers-tageting-crypto.html) The attack involves multiple [stages,](https://www.elastic.co/security-labs/elastic-catches-dprk-passing-out-kandykorn) utilizing Python scripts and reflective loading for execution. Additionally, an Android spyware variant called FastViewer, linked to a North Korean threat group called [Kimsuky,](https://izoologic.com/2022/11/08/north-korean-kimsuky-group-used-three-malware-strains-in-attacks/) has been discovered with updated functionality. The spyware abuses Android's accessibility services to gather sensitive data and download a second-stage malware, FastSpy. The new version integrates [FastSpy's](https://izoologic.com/2022/11/08/north-korean-kimsuky-group-used-three-malware-strains-in-attacks/)  functionality into FastViewer, eliminating the need for additional downloads. The hack was [discovered](https://www.elastic.co/security-labs/elastic-catches-dprk-passing-out-kandykorn) when Elastic Security Labs was analyzing attempts to load binary into memory of a macOS endpoint. 

## Attackers

   - North Korean Lazarus Group is suspected to be behind the theft.
   - State-sponsored threat actors from the Democratic People's Republic of Korea.

## Losses

There is No monetary loss reported.

## Timeline
   - **"April 2023:"** Elastic Security Labs [traced](https://www.elastic.co/security-labs/elastic-catches-dprk-passing-out-kandykorn) the Lazarus APT group's campaign using the KandyKorn malware through the RC4 key used for encryption in the SUGARLOADER and KandyKorn C2. The threat is ongoing, and there is ongoing development of tools and techniques by the attackers.
   - **"July 2023:"** There a subReditts user reports being contacted to solve a Python coding [challenge](https://www.elastic.co/security-labs/elastic-catches-dprk-passing-out-kandykorn.) appearing to be for a speedtest.  	 	
   - **"October 31, 2023:"** Elastic Security Lab releases an article discovering KandyKorn hack and explains the five phases KandyKorn uses.

## Security Failure Causes

By using social engineering the intrusion was able to utilize both custom and open source tools for gaining initial access and carrying out post-exploitation activities. Some of the security failures in this hack are connected to the following:

   - **Inadequate File and Process Monitoring:**
The successful attack can be attributed to the inadequate monitoring of file activities and process execution within the system.
   - **Lack of Memory Protection Mechanisms:**
The absence of robust memory protection mechanisms allowed the malware to operate stealthily within the system's memory, evading detection by traditional security controls.
   - **Failure in Network Traffic Monitoring:**
The attack's success can be traced to the failure to detect and block suspicious outbound communications with remote servers.
   - **Daisy-Chaining Payloads Without Interruption:**
The attackers successfully progressed through multiple stages of the attack due to the failure to detect and interrupt the daisy-chaining of payloads.
