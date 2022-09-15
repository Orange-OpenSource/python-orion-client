#!/usr/bin/env python3

# Software Name: ngsildclient
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

from typing import Tuple
from ngsildclient import Entity, Client


def build_entity(room: Tuple) -> Entity:
    name, temp, pressure = room
    e = Entity("RoomObserved", name)
    e.prop("temperature", temp)
    e.prop("pressure", pressure)
    return e


def main():
    client = Client()
    rooms = [("Room1", 23.1, 720), ("Room2", 21.8, 711)]
    entities = [build_entity(room) for room in rooms]
    client.upsert(entities)


if __name__ == "__main__":
    main()
