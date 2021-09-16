#!/usr/bin/env python3

# Software Name: python-orion-client
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battelo@orange.com> et al.
# SPDX-License-Identifier: Apache-2.0


from datetime import datetime, date, time
from geojson import Point, LineString, Polygon
from typing import Any, Union
from orionldclient.utils import iso8601, urnprefix
from .exceptions import *
from .constants import *
from .ngsidict import NgsiDict


def build_property(
    value: Any,
    unitcode: str = None,
    observedat: Union[str, datetime] = None,
    datasetid: str = None,
    userdata: NgsiDict = NgsiDict(),
) -> NgsiDict:
    property: NgsiDict = NgsiDict()
    property["type"] = AttrType.PROP.value  # set type
    if isinstance(value, (int, float, bool, str, list, dict)):
        v = value
    else:
        raise NgsiUnmatchedAttributeTypeError(
            f"Cannot map {type(value)} to NGSI type. {value=}"
        )
    property["value"] = value  # set value
    if unitcode is not None:
        property[META_ATTR_UNITCODE] = unitcode
    if observedat is not None:
        if isinstance(observedat, datetime):
            observedat = iso8601.from_datetime(observedat)
        property[META_ATTR_OBSERVED_AT] = observedat
    if datasetid is not None:
        property[META_ATTR_DATASET_ID] = urnprefix(datasetid)
    if userdata:
        property |= userdata
    return property


def build_geoproperty(value: Any) -> NgsiDict:
    property: NgsiDict = NgsiDict()
    property["type"] = AttrType.GEO.value  # set type
    if isinstance(value, (Point, LineString, Polygon)):
        geometry = value
    elif (
        isinstance(value, tuple) and len(value) == 2
    ):  # simple way for a location Point
        lat, lon = value
        geometry = Point((lon, lat))
    else:
        raise NgsiUnmatchedAttributeTypeError(
            f"Cannot map {type(value)} to NGSI type. {value=}"
        )
    property["value"] = geometry  # set value
    return property


def build_temporal_property(value: Any) -> NgsiDict:
    # TODO : handle Date and Time
    property: NgsiDict = NgsiDict()
    property["type"] = AttrType.TEMPORAL.value  # set type
    if isinstance(value, datetime):
        v = {
            "@type": TemporalType.DATETIME.value,
            "@value": iso8601.from_datetime(value),
        }
    elif isinstance(value, date):
        v = {
            "@type": TemporalType.DATE.value,
            "@value": iso8601.from_date(value),
        }
    elif isinstance(value, time):
        v = {
            "@type": TemporalType.TIME.value,
            "@value": iso8601.from_time(value),
        }
    elif isinstance(value, str):
        try:
            temporaltype = iso8601.parse(value)
        except ValueError as e:
            raise NgsiDateFormatError from e
        v = {
            "@type": temporaltype.value,
            "@value": value,
        }
    else:
        raise NgsiUnmatchedAttributeTypeError(
            f"Cannot map {type(value)} to NGSI type. {value=}"
        )
    property["value"] = v  # set value
    return property


def build_relationship(
    value: str,
    observedat: Union[str, datetime] = None,
    userdata: NgsiDict = NgsiDict(),
) -> NgsiDict:
    property: NgsiDict = NgsiDict()
    property["type"] = AttrType.REL.value  # set type
    property["object"] = urnprefix(value)  # set value
    if observedat is not None:
        if isinstance(observedat, datetime):
            observedat = iso8601.from_datetime(observedat)
        property[META_ATTR_OBSERVED_AT] = observedat
    if userdata:
        property |= userdata
    return property
