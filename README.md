# Spot Edit

A simple, lean AI-powered document editing tool that identifies and updates key fields in documents through natural language chat. Save document templates once, reuse them repeatedly.

## Overview

Spot Edit is a focused document editing assistant built around a straightforward workflow: upload a document, confirm the fields AI detects, save it as a template, then reuse it anytime by telling the AI what needs to change in plain English. The approach is designed to be simple, repeatable, and effective.

## Core Concept

The project centers on four key principles:

1. **Simple & Lean**: Minimal interface, maximum utility. No bloat, just effective document editing.
2. **Smart Field Detection**: Upload any document (with automatic text conversion if needed), and the AI identifies key fields and areas that need updating.
3. **Human-in-the-Loop**: You confirm which fields the AI detects before they become editable—ensuring accuracy and control.
4. **Template Reuse**: Save documents with their field mappings once, then reuse them repeatedly with natural language updates.

## How It Works

### Initial Document Setup
1. **Upload Document**: Drop your document into the chat window (supports various formats with automatic text conversion)
2. **AI Field Detection**: The AI automatically analyzes the document and identifies key editable fields (names, dates, prices, company info, etc.)
3. **Confirm Fields (HITL)**: Review and confirm which fields the AI found are the ones you want to make editable—this human-in-the-loop step ensures accuracy
4. **Save Template**: Once confirmed, the document and its identified variable fields are saved for future reuse

### Making Updates
1. **Load Saved Document**: Pull up any previously saved document template
2. **Tell the Agent**: Describe your changes in natural language (e.g., "update the contract date to March 15, 2024" or "change client name to Acme Corp")
3. **AI Updates Fields**: The agent intelligently updates the confirmed fields throughout the document
4. **Download**: Export your updated document with all changes applied

## Key Features

- **Document Upload & Conversion**: Accept various document formats, automatically convert to text for processing
- **AI-Powered Field Detection**: Automatically identifies key editable fields (names, dates, prices, addresses, etc.)
- **Human-in-the-Loop Confirmation**: Review and confirm AI-detected fields before saving—you stay in control
- **Document Templates & Storage**: Save documents with their confirmed field mappings for easy reuse
- **Natural Language Commands**: No complex syntax—just tell the agent what you want in plain English
- **Multi-Field Updates**: Update multiple related fields across the document in one operation
- **Template Library**: Access and reuse your saved document templates anytime
- **Export & Download**: Get your updated documents in the original format

## Design Philosophy

- **Simplicity First**: Every feature must earn its place. If it doesn't directly serve the core workflow, it doesn't belong.
- **Reliable & Repeatable**: The same input should produce predictable, consistent results.
- **Focused Scope**: Do one thing exceptionally well—AI-assisted document field updates.

## Use Cases

- **Contract Management**: Upload a contract template once, then quickly generate new versions by updating client names, dates, and terms
- **Invoice Generation**: Save an invoice template and update amounts, dates, and client details for each new invoice
- **Proposal Customization**: Maintain proposal templates and customize company names, project details, and pricing per client
- **Form Processing**: Identify form fields once, then rapidly fill different versions with updated information
- **Report Updates**: Save report templates and update key metrics, dates, and data points as needed
- **Document Localization**: Update addresses, currencies, and region-specific information across document sets

## Technology Approach

The technical stack will be chosen to support the core goals of simplicity and repeatability:
- Lightweight document parsing and text extraction
- LLM integration for natural language understanding and field identification
- Simple storage system for document templates and field mappings
- Intuitive UI for document upload, field confirmation, and chat interaction
- Minimal dependencies, maximum reliability

## Getting Started

*This section will be populated as the project develops.*

## Contributing

*Contribution guidelines will be added as the project matures.*

## License

*License to be determined.*
