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

import json

from copy import deepcopy
from datetime import datetime
from typing import Any, Union

from .exceptions import *
from .constants import *
from .attribute import *
from .ngsidict import NgsiDict


class ContextBuilder:

    DEFAULT = [
        "https://schema.lab.fiware.org/ld/context",
        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
    ]

    EMPTY = []

    _ctx: list[str] = None

    def __init__(self, ctx: list[str] = None):
        self._ctx = ContextBuilder.DEFAULT if ctx is None else ctx

    def add(self, uri: str):
        self._ctx.append(uri)
        return self

    def remove(self, uri: str):
        self._ctx.remove(uri)
        return self

    def __repr__(self):
        return self._ctx.__repr__()

    def build(self):
        return self._ctx


class Entity:
    def __init__(
        self,
        id: str,
        type: str,
        context: list = ContextBuilder().build(),
        contextfirst: bool = False,
    ):
        self.contextfirst = contextfirst  # TODO : move at api level
        self._payload: NgsiDict = NgsiDict(
            {"@context": context, "id": Urn.prefix(id), "type": type}
        )

    @classmethod
    def from_dict(cls, entity: dict):
        if not entity.get("id", None):
            raise NgsiMissingIdError()
        if not entity.get("type", None):
            raise NgsiMissingTypeError()
        if not entity.get("@context", None):
            raise NgsiMissingContextError()
        instance = cls(None, None)  # id and type will be overwritten next line
        instance._payload |= entity
        return instance

    @classmethod
    def load(cls, filename: str):
        with open(filename, "r") as fp:
            d = json.load(fp)
            return cls.from_dict(d)

    @property
    def id(self):
        return self._payload["id"]

    @property
    def type(self):
        return self._payload["type"]

    @property
    def context(self):
        return self._payload["@context"]

    def getattr(self, attr: str):
        return self._payload.get(attr)

    def setattr(self, attr: str, value: Any):
        self._payload[attr] = value

    def prop(
        self,
        name: str,
        value: Any,
        unitcode: str = None,
        observed_at: Union[str, datetime] = None,
        dataset_id: str = None,
        userdata: NgsiDict = NgsiDict(),
    ):
        self._payload.prop(name, value, unitcode, observed_at, dataset_id, userdata)
        return self._payload[name]

    def gprop(self, name: str, value: Any):
        self._payload.gprop(name, value)
        return self._payload[name]

    def tprop(self, name: str, value: Any):
        # TODO : handle Date and Time
        self._payload.tprop(name, value)
        return self._payload[name]

    def rel(
        self,
        name: str,
        value: str,
        observed_at: Union[str, datetime] = None,
        userdata: NgsiDict = NgsiDict(),
    ):
        self._payload.rel(name, value, observed_at, userdata)
        return self._payload[name]

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.type == other.type and self.id == other.id

    def __repr__(self):
        return self._payload.__repr__()

    def to_dict(self, contextfirst=False) -> NgsiDict:
        if contextfirst:
            return self._payload
        ctx = self._payload[META_ATTR_CONTEXT]
        payload = deepcopy(self._payload)
        del payload[META_ATTR_CONTEXT]
        payload[META_ATTR_CONTEXT] = ctx
        return payload

    def to_json(self, *args, **kwargs):
        """Returns the datamodel in json format"""
        payload = self.to_dict(self.contextfirst)
        return payload.to_json(*args, **kwargs)

    def pprint(self):
        """Returns the datamodel pretty-json-formatted"""
        print(self.to_json(indent=2))

    def save(self, filename: str, indent=2):
        payload = self.to_dict(self.contextfirst)
        with open(filename, "w") as fp:
            json.dump(payload, fp, default=str, ensure_ascii=False, indent=indent)
