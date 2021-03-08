# samples

This repository is full of various code samples.

## bootstrap.sh
This file serves as the key component of a Vagrant-based DevOps provisioning process for Drupal 7 development. Please take a look at the "main" section of the script at the bottom of the file. This code sample highlights how I like to structure my code in a readable way.

## esrifield
This sample demonstrates some of my PHP programming within the broader Drupal framework to define custom field types for Drupal's field API, utilizing dyanmic form loading for the configuration of said field. esrifield is designed to be used with ESRI's ArcGIS server, particularly their REST endpoints. It allows the selection of data elements within an ArcGIS endpoint to be selected from within Drupal and supports rendering those data elements within Drupal.

## Flask
Flask is a Python based micro-framework for developing web applications. It has become my goto choice for small scale and lightweight utilities.

### Gooclean
This project works in conjuction with cron jobs that connect to a Google domain to retrieve lists of suspended and expiring users in order to determine which Google Drive files that are still shared with other users are going to be deleted. _Goo_gle _Clean_up was developed to give users the ability to claim files that are shared with them before they are deleted. This is a simple Flask app that demonstrates my use of an ORM to support the front-end implementation for this process. It relies on system calls to underlying scripts to execute the necessary file transfers within the Google domain.

