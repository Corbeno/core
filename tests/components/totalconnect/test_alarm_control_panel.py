"""Tests for the TotalConnect alarm control panel device."""
from unittest.mock import patch

import pytest

from homeassistant.components.alarm_control_panel import DOMAIN as ALARM_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_FRIENDLY_NAME,
    SERVICE_ALARM_ARM_AWAY,
    SERVICE_ALARM_ARM_HOME,
    SERVICE_ALARM_ARM_NIGHT,
    SERVICE_ALARM_DISARM,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_CUSTOM_BYPASS,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMING,
    STATE_ALARM_DISARMED,
    STATE_ALARM_DISARMING,
    STATE_ALARM_TRIGGERED,
)
from homeassistant.exceptions import HomeAssistantError

from .common import (
    LOCATION_ID,
    RESPONSE_ARM_FAILURE,
    RESPONSE_ARM_SUCCESS,
    RESPONSE_ARMED_AWAY,
    RESPONSE_ARMED_CUSTOM,
    RESPONSE_ARMED_NIGHT,
    RESPONSE_ARMED_STAY,
    RESPONSE_ARMING,
    RESPONSE_DISARM_FAILURE,
    RESPONSE_DISARM_SUCCESS,
    RESPONSE_DISARMED,
    RESPONSE_DISARMING,
    RESPONSE_SUCCESS,
    RESPONSE_TRIGGERED_CARBON_MONOXIDE,
    RESPONSE_TRIGGERED_FIRE,
    RESPONSE_TRIGGERED_POLICE,
    RESPONSE_UNKNOWN,
    RESPONSE_USER_CODE_INVALID,
    setup_platform,
)

ENTITY_ID = "alarm_control_panel.test"
CODE = "-1"
DATA = {ATTR_ENTITY_ID: ENTITY_ID}


async def test_attributes(hass):
    """Test the alarm control panel attributes are correct."""
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        return_value=RESPONSE_DISARMED,
    ) as mock_request:
        await setup_platform(hass, ALARM_DOMAIN)
        state = hass.states.get(ENTITY_ID)
        assert state.state == STATE_ALARM_DISARMED
        mock_request.assert_called_once()
        assert state.attributes.get(ATTR_FRIENDLY_NAME) == "test"

        entity_registry = await hass.helpers.entity_registry.async_get_registry()
        entry = entity_registry.async_get(ENTITY_ID)
        # TotalConnect alarm device unique_id is the location_id
        assert entry.unique_id == LOCATION_ID


async def test_arm_home_success(hass):
    """Test arm home method success."""
    responses = [RESPONSE_DISARMED, RESPONSE_ARM_SUCCESS, RESPONSE_ARMED_STAY]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED

        await hass.services.async_call(
            ALARM_DOMAIN, SERVICE_ALARM_ARM_HOME, DATA, blocking=True
        )

        await hass.async_block_till_done()
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_ARMED_HOME


async def test_arm_home_failure(hass):
    """Test arm home method failure."""
    responses = [RESPONSE_DISARMED, RESPONSE_ARM_FAILURE, RESPONSE_DISARMED]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED

        with pytest.raises(HomeAssistantError) as err:
            await hass.services.async_call(
                ALARM_DOMAIN, SERVICE_ALARM_ARM_HOME, DATA, blocking=True
            )
            await hass.async_block_till_done()
        assert f"{err.value}" == "TotalConnect failed to arm home test."
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED


async def test_arm_home_invalid_usercode(hass):
    """Test arm home method with invalid usercode."""
    responses = [RESPONSE_DISARMED, RESPONSE_USER_CODE_INVALID, RESPONSE_DISARMED]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED

        with pytest.raises(HomeAssistantError) as err:
            await hass.services.async_call(
                ALARM_DOMAIN, SERVICE_ALARM_ARM_HOME, DATA, blocking=True
            )
            await hass.async_block_till_done()
        assert f"{err.value}" == "TotalConnect failed to arm home test."
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED


async def test_arm_away_success(hass):
    """Test arm away method success."""
    responses = [RESPONSE_DISARMED, RESPONSE_ARM_SUCCESS, RESPONSE_ARMED_AWAY]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED

        await hass.services.async_call(
            ALARM_DOMAIN, SERVICE_ALARM_ARM_AWAY, DATA, blocking=True
        )
        await hass.async_block_till_done()
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_ARMED_AWAY


async def test_arm_away_failure(hass):
    """Test arm away method failure."""
    responses = [RESPONSE_DISARMED, RESPONSE_ARM_FAILURE, RESPONSE_DISARMED]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED

        with pytest.raises(HomeAssistantError) as err:
            await hass.services.async_call(
                ALARM_DOMAIN, SERVICE_ALARM_ARM_AWAY, DATA, blocking=True
            )
            await hass.async_block_till_done()
        assert f"{err.value}" == "TotalConnect failed to arm away test."
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED


async def test_disarm_success(hass):
    """Test disarm method success."""
    responses = [RESPONSE_ARMED_AWAY, RESPONSE_DISARM_SUCCESS, RESPONSE_DISARMED]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_ARMED_AWAY

        await hass.services.async_call(
            ALARM_DOMAIN, SERVICE_ALARM_DISARM, DATA, blocking=True
        )
        await hass.async_block_till_done()
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED


async def test_disarm_failure(hass):
    """Test disarm method failure."""
    responses = [RESPONSE_ARMED_AWAY, RESPONSE_DISARM_FAILURE, RESPONSE_ARMED_AWAY]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_ARMED_AWAY

        with pytest.raises(HomeAssistantError) as err:
            await hass.services.async_call(
                ALARM_DOMAIN, SERVICE_ALARM_DISARM, DATA, blocking=True
            )
            await hass.async_block_till_done()
        assert f"{err.value}" == "TotalConnect failed to disarm test."
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_ARMED_AWAY


async def test_disarm_invalid_usercode(hass):
    """Test disarm method failure."""
    responses = [RESPONSE_ARMED_AWAY, RESPONSE_USER_CODE_INVALID, RESPONSE_ARMED_AWAY]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_ARMED_AWAY

        with pytest.raises(HomeAssistantError) as err:
            await hass.services.async_call(
                ALARM_DOMAIN, SERVICE_ALARM_DISARM, DATA, blocking=True
            )
            await hass.async_block_till_done()
        assert f"{err.value}" == "TotalConnect failed to disarm test."
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_ARMED_AWAY


async def test_arm_night_success(hass):
    """Test arm night method success."""
    responses = [RESPONSE_DISARMED, RESPONSE_ARM_SUCCESS, RESPONSE_ARMED_NIGHT]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED

        await hass.services.async_call(
            ALARM_DOMAIN, SERVICE_ALARM_ARM_NIGHT, DATA, blocking=True
        )

        await hass.async_block_till_done()
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_ARMED_NIGHT


async def test_arm_night_failure(hass):
    """Test arm night method failure."""
    responses = [RESPONSE_DISARMED, RESPONSE_ARM_FAILURE, RESPONSE_DISARMED]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED

        with pytest.raises(HomeAssistantError) as err:
            await hass.services.async_call(
                ALARM_DOMAIN, SERVICE_ALARM_ARM_NIGHT, DATA, blocking=True
            )
            await hass.async_block_till_done()
        assert f"{err.value}" == "TotalConnect failed to arm night test."
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED


async def test_arming(hass):
    """Test arming."""
    responses = [RESPONSE_DISARMED, RESPONSE_SUCCESS, RESPONSE_ARMING]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMED

        await hass.services.async_call(
            ALARM_DOMAIN, SERVICE_ALARM_ARM_NIGHT, DATA, blocking=True
        )
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_ARMING


async def test_disarming(hass):
    """Test disarming."""
    responses = [RESPONSE_ARMED_AWAY, RESPONSE_SUCCESS, RESPONSE_DISARMING]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_ARMED_AWAY

        await hass.services.async_call(
            ALARM_DOMAIN, SERVICE_ALARM_DISARM, DATA, blocking=True
        )
        assert hass.states.get(ENTITY_ID).state == STATE_ALARM_DISARMING


async def test_triggered_fire(hass):
    """Test triggered by fire."""
    responses = [RESPONSE_TRIGGERED_FIRE]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        state = hass.states.get(ENTITY_ID)
        assert state.state == STATE_ALARM_TRIGGERED
        assert state.attributes.get("triggered_source") == "Fire/Smoke"


async def test_triggered_police(hass):
    """Test triggered by police."""
    responses = [RESPONSE_TRIGGERED_POLICE]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        state = hass.states.get(ENTITY_ID)
        assert state.state == STATE_ALARM_TRIGGERED
        assert state.attributes.get("triggered_source") == "Police/Medical"


async def test_triggered_carbon_monoxide(hass):
    """Test triggered by carbon monoxide."""
    responses = [RESPONSE_TRIGGERED_CARBON_MONOXIDE]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        state = hass.states.get(ENTITY_ID)
        assert state.state == STATE_ALARM_TRIGGERED
        assert state.attributes.get("triggered_source") == "Carbon Monoxide"


async def test_armed_custom(hass):
    """Test armed custom."""
    responses = [RESPONSE_ARMED_CUSTOM]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        state = hass.states.get(ENTITY_ID)
        assert state.state == STATE_ALARM_ARMED_CUSTOM_BYPASS


async def test_unknown(hass):
    """Test unknown arm status."""
    responses = [RESPONSE_UNKNOWN]
    with patch(
        "homeassistant.components.totalconnect.TotalConnectClient.TotalConnectClient.request",
        side_effect=responses,
    ):
        await setup_platform(hass, ALARM_DOMAIN)
        state = hass.states.get(ENTITY_ID)
        assert state.state == "unknown"
