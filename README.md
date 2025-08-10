# ieditllm
CLI tools to improve latex documents using LLMs

Overview
iedit is a CLI tool able for editing Latex files to improve their form, syntax and grammar. Its aim is to provide a polished version of the document, similar to the ones published at top scientific conferences. The tool is inspired by ispell but it targets signifiantly more complex changes, thanks to the usage of AI.

Main features
iedit will allow you to:

- connect to the AI models provided by Amazon Bedrock
- specify which model to use to polish the doc
- see the changes one by one before they are applied to the files (with your confirmation)
- make localized changes in the doc, while offering sufficient context to evaluate the impact
- specify folders containing several latex documents to polish all of them
- retain exactly the numerical values provided in the Latex documents

Installation
You can easily install iedit using pip install iedit.