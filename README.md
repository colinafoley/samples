# samples

This repository is full of various code samples.

## bootstrap.sh
This file serves as the key component of a Vagrant-based DevOps provisioning process for Drupal 7 development. Please take a look at the "main" section of the script at the bottom of the file. This code sample highlights how I like to structure my code in a readable way.

## esrifield
This sample demonstrates some of my PHP programming within the broader Drupal framework to define custom field types for Drupal's field API, utilizing dyanmic form loading for the configuration of said field. esrifield is designed to be used with ESRI's ArcGIS server, particularly their REST endpoints. It allows the selection of data elements within an ArcGIS endpoint to be selected from within Drupal and supports rendering those data elements within Drupal.

## Flask
Flask is a Python based micro-framework for developing web applications. It has become my goto choice for small scale and lightweight utilities.

### gooclean
This project works in conjuction with cron jobs that connect to a Google domain to retrieve lists of suspended and expiring users in order to determine which Google Drive files that are still shared with other users are going to be deleted. *Goo*gle Sharing *Clean*up was developed to give users the ability to claim files that are shared with them before they are deleted. This is a simple Flask app that demonstrates my use of an ORM to support the front-end implementation for this process. It relies on system calls to underlying scripts to execute the necessary file transfers within the Google domain.

### elastalert-rule-manager
This sample is a small selection of an application used to provide a web front-end to a utility developed by Yelp called elastalert. elastalert is used for alerting based off of data within an Elastic search cluster. The rule manager sits on top of a deployment of elastalert to allow for web based editing, testing, and management of the required YAML rules files that elastalert needs to perform alerting. This tool uses a flatfile system for storage so that it can directly interface with the YAML rule files. The code selection provided here shows my use of Object Oriented Programming to abstract away many of the complex file handling needed to interact with YAML files as a rules "database". There is a lot of work that could be done to improve this project, but I've included it nonetheless due to its unconventional nature.
