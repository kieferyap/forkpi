# ForkPi 

ForkPi: A door access control system that is more accessible to the world. ForkPi stands for **F**ingerprint, **O**LED, **R**FID, **K**eypad, and Raspberry **Pi**.

-----------------------

## Overview

### Motivation

Modern keyless door access control systems remain largely inaccessible to the public, due to their high cost and low transparency. Our system, ForkPi, is a cost-effective solution that is designed to be intuitive to use, and easy to customize or extend.

### Authentication Mechanisms

It supports five different authentication mechanisms involving three factors: RFID, fingerprint and PIN. The single-door access control provided by SpoonPi easily scales to multiple doors via the accompanying web app, ForkPi, which provides secure, centralized management of multiple SpoonPis over a local network.

### Platform

We chose the Raspberry Pi for our platform because it is open-source, accessible, and easy to set up.

-----------------------

## Technical Specifications

Our system has two types of Raspberry Pis: the ForkPi and the SpoonPis. There is only one ForkPi unit in the system, and it has multiple SpoonPi units associated with it, with each SpoonPi associated with each door to be secured. All Raspberry Pis, and the admin's computer, are connected to the same network, either wirelessly or through a cable.

![forkpi-spoonpi-architecture](https://github.com/crentagon/forkpi/blob/master/images/forkpi-spoonpi-architecture.png)

### ForkPi (Python 3.0, Django 2.0)

#### ForkPi Overview

The ForkPi unit functions as both a web and database server. The web server runs a locally accessible website where one can register new users into the system, view logs, and perform other administrative actions. The web server has an underlying database run by PostgreSQL. Human administrators view ForkPi as a web server, while SpoonPis view ForkPi as a database server. The duty of ForkPi is to create a centralized interface between admins and the SpoonPi units.

#### Accessing ForkPi

ForkPi is addressed within the local network using the name `forkpi.local`. The web server runs in the default HTTP port (`80`), so admins will access the web app using the URL `http://forkpi.local/`. The database server runs in the port `5432`, so SpoonPis will access the database using the host name `forkpi.local` and the port number `5432`.

#### Peripherals Attached

A dedicated ForkPi unit does not require the presence of a keypad nor an OLED display, but it requires having the following peripherals attached:

- **RFID Scanner**: for scanning the UIDs of RFID tags to be registered 
- **Fingerprint Scanner**: for the enrollment of new fingerprints.

### SpoonPi (Python 3.0)

#### SpoonPi Overview

The SpoonPi units serve as the media for door authentication, and are responsible for granting or denying access through doors. There are as many SpoonPis as doors to be secured.

#### Authenticating with SpoonPi

Each SpoonPi unit needs to register itself first with the ForkPi unit before any authentication can be done. SpoonPi performs authentication by communicating with the hardware components (e.g. RFID scanner) to get the input credentials (e.g. RFID UID), then querying the ForkPi database to check if it is valid. For fingerprint authentication, the verification is done at the SpoonPi side instead of the ForkPi side, because the matching is not a simple string comparison; fingerprint templates have to be uploaded to the scanner, where the actual matching takes place.

#### Feasibility of ForkPi and SpoonPi in the same Raspberry Pi

While it is possible to have both the ForkPi and SpoonPi in a single Raspberry Pi to save cost, it must be noted that in this setup, while a new user is being enrolled, the SpoonPi process has to be stopped temporarily because the scanner peripherals (RFID and fingerprint) cannot accommodate both the SpoonPi and the ForkPi communicating with them at the same time.

#### Peripherals Attached

A SpoonPi unit requires having the following peripherals attached:

- **Fingerprint Scanner**: for identifying the fingerprint presented
- **OLED**: for displaying the current status of the transaction
- **RFID Scanner**: for scanning the UID of the RFID tag presented
- **Keypad**: for entering the PIN

-----------------------

## Screenshots
[In progress]

-----------------------

## Installation Guide
[In progress]

