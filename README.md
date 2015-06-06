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

### ForkPi (Python 3.2.3, Django 1.7.1)

#### ForkPi Overview

The ForkPi unit functions as both a web and database server. The web server runs a locally accessible website where admins can register new users into the system, view logs, and perform other administrative actions. The web server has an underlying database run by PostgreSQL. Human administrators view ForkPi as a web server, while SpoonPis view ForkPi as a database server. The duty of ForkPi is to create a centralized interface between admins and the SpoonPi units.

#### Accessing ForkPi

ForkPi is addressed within the local network using the name `forkpi.local`. The web server runs in the default HTTP port (`80`), so admins will access the web app using the URL `http://forkpi.local/`. The database server runs in the port `5432`, so SpoonPis will access the database using the host name `forkpi.local` and the port number `5432`.

#### Peripherals Attached

A dedicated ForkPi unit does not require the presence of a keypad nor an OLED display, but it requires having the following peripherals attached:

- **RFID Scanner**: for scanning the UIDs of RFID tags to be registered 
- **Fingerprint Scanner**: for the enrollment of new fingerprints.

### SpoonPi (Python 3.2.3)

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

## Screenshots and Usage

### ForkPi

![forkpi-use-case](https://github.com/crentagon/forkpi/blob/master/images/forkpi-use-case.png)

#### Adding a new user
![add-keypair](https://github.com/crentagon/forkpi/blob/master/images/add-keypair.png)

The primary function of admins is to manage authentication credentials and permissions across the system. The term "keypair" will be used hereon to refer to a set of one, two, or three authentication credentials that users will present to the SpoonPi door controllers in order to be granted access.

Even in the case where all three fields of PIN, RFID UID, and fingerprint template are filled, only two credentials will be needed to be granted access by SpoonPi.

When an admin logs in, they will be redirected to the Keypairs page, where they can see a list of all registered keypairs, and register new keypairs. To register new keypairs, admins would need to specify a unique, non-blank name for the keypair (e.g. the person's full name or ID number), and enter either an RFID UID or a fingerprint template.

Neither of these RFID and fingerprint fields are meant to be inputted manually; there is a corresponding scan button for each field to detect the UID (for RFID), or to scan a finger and return the template (for fingerprint).

The PIN is optional, but if entered, it has to consist of at least 4 digits. Once a keypair has been added, the username of the admin that created it is stored, so that other admins can determine who to hold accountable if an unauthorized person is granted a keypair.

#### Editing user credentials

After a keypair has been created, its name and credentials can still be edited at a later time.

![edit-keypair](https://github.com/crentagon/forkpi/blob/master/images/edit-keypair.png)
![edit-credentials](https://github.com/crentagon/forkpi/blob/master/images/edit-credentials.png)

There are many cases where users would need to edit their keypair (e.g. they forget their PIN, or lose their RFID tag). To prevent the admins from editing users' keypairs without their consent, our system requires the user to present one credential before they can edit their keypair. This does not necessarily have to be the credential to be changed, except in the case where they only have one credential.

If RFID is the sole credential of the user and they lose it, then the admin can just deactivate the keypair and create a new keypair with a different RFID UID. The same goes for single-factor fingerprint, although users do not normally need to change their registered fingerprint. Once a keypair has been edited, the username of the admin that modified the keypair is updated so that he/she can be held liable for any unauthorized changes.

A keypair can be temporarily deactivated (e.g. if the user leaves the community, or the keypair has been compromised). After a keypair has been deactivated, it will no longer be accepted in any door. This change can be reversed by reactivating the keypair. Deactivation and reactivation can be done by any admin without the explicit consent of the keypair's owner. Since this can also be considered as an edit action, the username of the admin that performed the change will be stored with the keypair.

#### Security Logs
![logs-show](https://github.com/crentagon/forkpi/blob/master/images/logs-show.png)

In an access control system, it is important to be able to check who has entered a room and at what time. For example, if something important gets stolen from a room, the search can be narrowed down to the people who have entered that room on that day. Even just knowing who has attempted to enter a door can be useful, in order to thwart users who are trying to gain unauthorized access through a door.

ForkPi allows admins to view all logs collected from all SpoonPis. This can be further sorted or filtered by date, the door concerned, the credentials entered, the keypair name (if access was allowed), or the reason for denial (if access was denied).

The RFID UID is the only credential that is visible in the logs, since admins might want to see if a certain RFID tag has been stolen and is being brute-forced. PINs are converted into a sequence of asterisks, while fingerprints are limited to a simple yes/no (if a finger was used in the authentication), since the actual fingerprint template is of no use here.

![logs-export](https://github.com/crentagon/forkpi/blob/master/images/logs-export.png)

Oftentimes, people other than admins would need to see these access logs for record keeping. For this purpose, admins can export logs to CSV (comma-separated values) format, exactly how it appears on the View Logs page, i.e. sorts and filters are preserved in the output. However, the columns showing details
about the authentication credentials used (PIN, RFID UID and Fingerprint) are removed, since this file would be viewable by a wider audience.

![logs-delete](https://github.com/crentagon/forkpi/blob/master/images/logs-delete.png)

After an admin has exported logs to CSV format and saved it to their computer, they have the option of deleting the now-obsolete logs, in order to save space on the ForkPi's SD card. Unlike deactivation, as in keypairs, this deletion is permanent and irreversible. Deletion of specific logs, or logs within a specific
date range is not allowed, to discourage admins from manually manipulating the content of the logs, e.g. making it look like user X never went through door Y.

#### Admin Registration
![show-users](https://github.com/crentagon/forkpi/blob/master/images/show-users.png)
![show-users](https://github.com/crentagon/forkpi/blob/master/images/show-users.png) (Change this to the "admin waiting approval" screen)

When someone signs up for an admin account, they need the approval of a super admin before they can become a regular admin. This is considered a sensitive operation, because if even regular admins can approve new
admins, the number of admins will grow very quickly, and some of those admins may not be persons that can be trusted with using the ForkPi system properly, or with good intent.

Ideally, there should be as few super admins as possible, but it is possible for a super admin to promote a regular admin into a super admin. This is useful for environments where there are two or more administrators, all of equal ranking, and hence need to be granted the same high level of power. A super admin can also be demoted by other super admins back into a regular admin. However, a super admin cannot demote his/herself.

### Security Options
![options](https://github.com/crentagon/forkpi/blob/master/images/options.png)

ForkPi admins can also change the global SpoonPi configuration through the Options page. There are a total of five settings that can be changed, which will be discussed later.

We decided to make this a super admin-only function, since a single change here immediately affects all SpoonPis in the system. Also, in the same web page is the "Regenerate secret key" button. When pressed, this resets the AES key used for encrypting the sensitive database fields, namely the PIN and RFID UID, of all keypairs. Nothing changes in the point of view of the admin, but in the underlying database, these fields change their values completely. We recommend regenerating the secret key every few months in order to keep these fields secured, and prevent brute force attacks on the encryption key.

### SpoonPi

#### Information
In registering a SpoonPi unit as a door, the admin must also give it a unique, non-blank name, usually the name of the room whose door it will be installed on. This name will be used in the ForkPi web app to refer to the door when linking or unlinking keypairs.

The door name can be changed later by running the registration script again, but passing it a different name. Under the hood, the SpoonPi unit uses its unique serial number when registering, so it knows if it has already been registered before. This serial number is also used so that SpoonPi only queries for keypairs that are linked to it in the database.

#### Transactions

In the SpoonPi application, a transaction is a single unit of work, which starts when SpoonPi begins waiting for a user to present a crendential, and ends with either allowing or denying the user, and then finally logging the transaction.

The flowchart below gives an overview of the main transaction loop. The process "Finish entering PIN" will be described later on using another flowchart. The three factors our system supports, RFID, fingerprint, and PIN, each have a thread dedicated to them. The alternative is to define an order in which the three factors should be presented, but we decided that any order imposed would be arbitrary and not intuitive to the users.

![spoonpi-flowchart](https://github.com/crentagon/forkpi/blob/master/images/spoonpi-flowchart.png)

#### Default Screen
![spoon-initial](https://github.com/crentagon/forkpi/blob/master/images/spoon-initial.png)

#### Entering the PIN
![spoon-pin](https://github.com/crentagon/forkpi/blob/master/images/spoon-pin.png)

#### Swiping the RFID Card
![spoon-rfid](https://github.com/crentagon/forkpi/blob/master/images/spoon-rfid.png)

The RFID security we implemented is simple in that only the UID is retrieved from the tag. Hence, a combination of RFID and PIN may be vulnerable to brute force attacks. To prevent this, we defined an attempt limit of 5 (which can be reconfigured via ForkPi options). If a registered RFID tag is presented but the wrong PIN is entered, the failed attempt streak counter will increment, and if this reaches 5, the SpoonPi unit will reject all further log-in attempts from that RFID tag. 

This lockout will expire after a certain amount of time, after which the RFID tag can be used normally again. Note that lockouts are local to a SpoonPi unit; an RFID tag locked out for a certain door can still be used in other doors.

#### Scanning Fingerprint
![spoon-fingerprint](https://github.com/crentagon/forkpi/blob/master/images/spoon-fingerprint.png)

In finding keypairs whose fingerprint template matches that of the finger presented to SpoonPi, the fingerprint thread queries ForkPi for all keypairs that have a non-blank fingerprint template field, and are linked to its door. Then, it registers the presented template onto the fingerprint scanner's onboard memory. It uploads the queried templates, and matches it with the presented template using the scanner's internal matching algorithm. It stores the keypair IDs of all matches in a list, then returns that to the main transaction process, which queries for keypairs whose ID is in the list of fingerprint matches.

#### Access Granted
![spoon-granted](https://github.com/crentagon/forkpi/blob/master/images/spoon-granted.png)

-----------------------

## Installation Guide
[In progress]

