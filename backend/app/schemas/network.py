"""📡 Schemas للشبكة"""
from datetime import datetime
from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    name:           str  = Field(..., min_length=1, max_length=255)
    ip_address:     str  = Field(..., min_length=7)
    hostname:       str | None = None
    mac_address:    str | None = None
    device_type:    str = "other"
    vendor:         str | None = None
    model:          str | None = None
    location:       str | None = None
    description:    str | None = None
    port:           int | None = None
    snmp_community: str | None = None
    tags:           list[str] = []
    parent_id:      str | None = None
    x_pos:          float = 0.0
    y_pos:          float = 0.0


class DeviceUpdate(BaseModel):
    name:           str | None = None
    ip_address:     str | None = None
    hostname:       str | None = None
    mac_address:    str | None = None
    device_type:    str | None = None
    vendor:         str | None = None
    model:          str | None = None
    location:       str | None = None
    description:    str | None = None
    port:           int | None = None
    snmp_community: str | None = None
    tags:           list[str] | None = None
    parent_id:      str | None = None
    x_pos:          float | None = None
    y_pos:          float | None = None


class DeviceOut(BaseModel):
    id:              str
    name:            str
    ip_address:      str
    hostname:        str | None
    mac_address:     str | None
    device_type:     str
    vendor:          str | None
    model:           str | None
    location:        str | None
    description:     str | None
    status:          str
    latency_ms:      float | None
    packet_loss_pct: float | None
    uptime_pct:      float | None
    cpu_pct:         float | None
    mem_pct:         float | None
    tags:            list
    parent_id:       str | None
    x_pos:           float
    y_pos:           float
    is_active:       bool
    created_at:      datetime | None

    model_config = {"from_attributes": True}
