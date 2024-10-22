---
title: Synthetic Data
mermaid: true
---

This page describes a pipeline for relevant token extraction from Large Language Models (LLMs) through the generation of synthetic data. The resulting synthetic dataset can be used for reducing computational costs in classification use cases. In addition to the overview diagram below, we provide links to all relevant scientific resources and tools we've built. For consistency across our examples, we focus on cyberattacks within the blockchain industry; however, this approach can be adapted to various use cases with minimal modifications to the prompts. All materials are released under the Unlicense public domain waiver.

## Overview Diagram

{{< mermaid >}}
flowchart TB
%% Nodes
    subgraph Data_Samples ["Data Samples"]
        Collect_Examples("Collect Examples")
        Deduplication_DataSamples("Deduplication")
    end
    subgraph Build_Extraction_Prompt ["Token Extraction Prompt"]
        Write_Instructions("Write Instructions")
        subgraph Add_Indicators ["Add Indicators"]
            direction TB
            Generate_Indicators("Generate Indicators")
            Summarization("Summarization")
        end
    end
    Synth_Data_Generation["Synthetic Data Generation"]
    Deduplication_GenerateData("Deduplication")
%% Connections
Collect_Examples --> Deduplication_DataSamples --> Synth_Data_Generation
Generate_Indicators --> Summarization
Write_Instructions --> Add_Indicators --> Synth_Data_Generation --> Deduplication_GenerateData
{{< /mermaid >}}

## Data Samples

Obtaining diverse data samples is as important as writing effective prompts. These samples will be inserted in batches at the Synthetic Data Generation stage. To ensure adequate randomization of order and guarantee single insertion, we compute unique identifiers derived from data sample hashes.

### Deduplication

We've built Deduplicated Insert Tool, a service designed to eliminate both duplicate and near-duplicate content, thereby ensuring diversity and token uniqueness in our dataset. This tool enables us to:

- Effectively handle duplicates and near-duplicates. Cosine distance provides a robust measure of semantic similarity between text samples, enabling identification and removal of redundant or nearly identical data points.
- Continuously measure token diversity. By tracking similarity scores during data collection, we can proactively assess and enhance the lexical and semantic richness of our dataset.
- Make real-time decisions on sample collection requirements. The deduplication process informs us when sufficient diversity has been achieved, allowing for the optimization of data collection efforts.

## Token Extraction Prompt

Well-crafted prompts help increase the reliability of synthetic data generation and raise the overall quality of the data. An extraction prompt not only acts as a set of instructions for an LLM, but also introduces tokens that might be missing in collected data and can compensate for potential bias present in data examples.

### Prompt Structure

A well-structured prompt includes 3 main components:

1. **Instructions** (Task Description & Critical Instructions)
1. **Indicators**
1. **Examples** (e.g., Social Media Messages)

### Instructions

This part is highly dependent on your topic and industry. However, there are a few common things you can reuse across all prompts. Adapt this section to your use case by replacing "cyberattacks" with your topic and "blockchain" with your industry.

#### Task Description Section

> Your task is to generate a list of social media platform messages to be used as early warning signals for identifying a cyberattack on a blockchain industry participant. Below are 2 lists. "Cyberattack Indicators" list contains signals that can lead to a financial or reputational loss. The other list, "Social Media Messages", contains social media platform messages about cyberattacks on a blockchain industry that happened in the past. Use "Cyberattack Indicators" and "Social Media Messages" to generate 100 new social media platform messages that could imply a cyberattack on a blockchain ecosystem participant, including very early stages of it.

💡 Since some data may be sensitive (e.g., data concerning cyberattacks), LLMs may refuse to generate synthetic samples. In such cases, try clarifying the purpose of the project:

> The generated synthetic data will be used for a classification task that is research-oriented. The data will not be used for any purpose other than research.`

####  Critical Instructions Section

This section is highly dependent not only on your industry, but also on the real data you have collected. It provides an opportunity to account for possible biases present in the Data Samples, such as named entities.

> Critical:
> 
> - Use modern vocabulary and writing style.
> - Leave Law Enforcement and Government Regulators' names unchanged, but replace other named entities (organization, person, location names, etc.) with fictional, but probable and modern ones.
> - The output must be a list of 100 newly generated social media platform messages without any explanations.

💡 You might need to adjust the language style if your industry made progress or expanded significantly since the earliest data point you have.

💡 Pay attention to the number of messages you want the LLM to generate at once. Depending on the size and the nature of your individual data examples, you might need to reduce the size of message batches to maintain the output data quality and the LLM service stability.

### Indicators

This compact prompt section lists concepts relevant to a given use case and serves several crucial purposes:

- Focuses the LLM's attention on a highly distilled collection of relevant tokens
- Highlights model features that are not well-pronounced in the data samples
- Compensates for biases and deficiencies in the data samples

#### Indicators Example

> Key blockchain ecosystem cyberattack indicators include unusual spikes in transaction volume, abnormal confirmation times, unexpected changes in mining difficulty, and suspicious smart contract interactions. Wallet-related red flags involve sudden activation of dormant addresses, unauthorized transactions, and compromised private keys. Exchange-specific indicators include rapid price fluctuations, withdrawal issues, and unexpected downtime. Infrastructure concerns manifest as unverified nodes, synchronization delays, and potential 51% attacks. Cross-chain vulnerabilities, security breaches, phishing attempts, and API compromises are critical to monitor. Community sentiment, governance irregularities, and blockchain explorer activity provide additional context for potential threats.

Although it is possible for a subject-matter expert to write this section manually, the idea is to use a few effective techniques described below to provide assurances for correctness and completeness of the resulting indicators.

#### Generate Indicators

The most obvious approach to extract native tokens is to ask an LLM to generate some relevant content. There are, however, a few important considerations to take into account when using this technique:

- Leverage multiple models trained on different datasets
- Select models with the most recent knowledge cut-off dates, especially for fast-changing industries and emergent topics
- Use different LLM service implementations, as they might have different optimizations and safeguards around your use cases.
- Consider adding an extra knowledge section with your relevant private data.
- Reference public knowledge, such as historical events that LLMs might be familiar with.
- Use resources you'd use to teach someone manual classification.

#### Indicators Generation Prompt Example

> Your task is to generate a list of Blockchain Ecosystem Cyberattack Indicators that could be spotted by looking at social media chatter, including very early stages of the attack. Blockchain ecosystem participants could include centralized and decentralized products, exchanges, protocols, wallets, smart contracts, bridges, oracles, developers, key people, etc. Information included below could help you reason about useful signals for monitoring reports on social media.
>
> # General Knowledge
> 
> article_text_1
> 
> article_text_2
> 
> ...
> 
> article_text_n
>
> # Historical Events
> 
> date_1 - named_entity_1
>
> date_2 - named_entity_2
> 
> ...
> 
> date_n - named_entity_n

#### Indicator Summarization

Resulting outputs from the indicator generation stage will probably include verbose descriptions with plenty of semantic duplicates. It is important to consolidate and refine the AI-generated content from the previous steps into a concise, non-redundant, highly condensed list of indicators that could be validated by the subject-matter expert. Here are the key points to keep in mind:

- Use a frontier model with:
  - Large context window
  - Good reasoning capabilities
  - Low-temperature setting
- Model's cut-off date is less critical for this step
- Aim for alignment between your understanding on what to consider important and the model's output
- Pay close attention to relevant concepts being left out or becoming too general. Refrain from manual additions. Instead, focus on improving your indicator generation prompts.
- You can also compare outputs from 2 different models. This helps ensure no important information was left behind.

#### Indicator Summarization Prompt Example

> Your task is to deduplicate and summarize a list of Blockchain Ecosystem Cyberattack Indicators you will find below. It's okay to merge similar ideas into one concept, but don't remove any ideas completely. Generate a succinct paragraph with densely packed indicators and associated concepts you will find below.
> 
> <list_of_indicators>

## Synthetic Data Generation

By combining the extraction prompt and randomized batches of data samples, we construct and send resulting batches to the LLMs that we want to extract tokens from. Even when backed by the same models, different LLM services might have unique implementations that affect the reliability of synthetic data generation. Consequently, fine-tuning the prompts may be necessary to achieve consistent output of diverse synthetic data across various LLM services.


## Final Prompt Example

> Your task is to generate a list of social media platform messages to be used as early warning signals for identifying a cyberattack on a blockchain industry participant. Below are 2 lists. "Cyberattack Indicators" list contains signals that can lead to a financial or reputational loss. The other list, "Social Media Messages", contains social media platform messages about cyberattacks on a blockchain industry that happened in the past. Use "Cyberattack Indicators" and "Social Media Messages" to generate 100 new social media platform messages that could imply a cyberattack on a blockchain ecosystem participant, including very early stages of it.
> 
> Critical:
>
> - Use modern vocabulary and writing style.
> - Leave Law Enforcement and Government Regulators' names unchanged, but replace other named entities (organization, person, location names, etc.) with fictional, but probable and modern ones.
> - The output must be a list of 100 newly generated social media platform messages without any explanations.
> 
> Cyberattack Indicators:
>
> Key blockchain ecosystem cyberattack indicators include unusual spikes in transaction volume, abnormal confirmation times, unexpected changes in mining difficulty, and suspicious smart contract interactions. Wallet-related red flags involve sudden activation of dormant addresses, unauthorized transactions, and compromised private keys. Exchange-specific indicators include rapid price fluctuations, withdrawal issues, and unexpected downtime. Infrastructure concerns manifest as unverified nodes, synchronization delays, and potential 51% attacks. Cross-chain vulnerabilities, security breaches, phishing attempts, and API compromises are critical to monitor. Community sentiment, governance irregularities, and blockchain explorer activity provide additional context for potential threats.
> 
> Social Media Messages:
>
> <Data Samples>

## Synthetic Data Deduplication

Using the same instruments and approach described in the Data Samples Deduplication section, we obtain a deduplicated and diverse synthetic dataset. After generating synthetic data batches, we pass the messages through the Deduplicated Insert Tool to eliminate duplicates and near-duplicates, thus maintaining the quality and diversity of the synthetic data. Vector similarity scores are continuously monitored during the deduplication phase, enabling real-time tracking of token diversity. This process allows us to dynamically assess whether additional synthetic samples are required or if the current dataset has achieved the desired level of diversity.
