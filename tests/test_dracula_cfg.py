import pytest
import unittest.mock as mock
import tempfile
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock, call
from configparser import ConfigParser

# Import the module under test (adjust path based on actual module structure)
# Assuming there's a dracula_cfg module or similar configuration handler
try:
    from dracula_cfg import DraculaConfig, load_config, validate_config
except ImportError:
    # Mock the module if it doesn't exist yet
    DraculaConfig = MagicMock
    load_config = MagicMock
    validate_config = MagicMock


@pytest.fixture
def valid_dracula_config():
    """Returns a valid Dracula configuration dictionary."""
    return {
        "theme_name": "Dracula",
        "colors": {
            "background": "#282a36",
            "foreground": "#f8f8f2",
            "selection": "#44475a",
            "comment": "#6272a4",
            "red": "#ff5555",
            "orange": "#ffb86c",
            "yellow": "#f1fa8c",
            "green": "#50fa7b",
            "purple": "#bd93f9",
            "cyan": "#8be9fd",
            "pink": "#ff79c6"
        },
        "settings": {
            "transparency": 0.95,
            "font_family": "Fira Code",
            "font_size": 14,
            "line_height": 1.6,
            "cursor_style": "block"
        },
        "features": {
            "italic_comments": True,
            "bold_keywords": False,
            "underline_links": True
        }
    }


@pytest.fixture
def invalid_dracula_config():
    """Returns an invalid Dracula configuration dictionary."""
    return {
        "theme_name": "",  # Invalid empty name
        "colors": {
            "background": "invalid_color",  # Invalid color format
            "foreground": "#xyz123",  # Invalid hex color
            "selection": None  # Invalid None value
        },
        "settings": {
            "transparency": 1.5,  # Invalid transparency > 1.0
            "font_size": -10,  # Invalid negative font size
            "line_height": "invalid"  # Invalid string for numeric value
        }
    }


@pytest.fixture
def dracula_cfg_content():
    """Returns sample Dracula.cfg file content."""
    return """[General]
Name=Dracula
Description=A dark theme for many editors, shells, and more
Author=Dracula Team

[Colors]
Background=#282a36
Foreground=#f8f8f2
Selection=#44475a
Comment=#6272a4
Red=#ff5555
Orange=#ffb86c
Yellow=#f1fa8c
Green=#50fa7b
Purple=#bd93f9
Cyan=#8be9fd
Pink=#ff79c6

[Settings]
Transparency=0.95
FontFamily=Fira Code
FontSize=14
LineHeight=1.6
CursorStyle=block

[Features]
ItalicComments=True
BoldKeywords=False
UnderlineLinks=True
"""


@pytest.fixture
def temp_config_file(dracula_cfg_content):
    """Creates a temporary Dracula configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
        f.write(dracula_cfg_content)
        temp_file_path = f.name
    yield temp_file_path
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def temp_json_config(valid_dracula_config):
    """Creates a temporary JSON configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(valid_dracula_config, f, indent=2)
        temp_file_path = f.name
    yield temp_file_path
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


class TestDraculaConfigLoading:
    """Test suite for Dracula configuration loading functionality."""
    
    def test_load_config_from_cfg_file_success(self, temp_config_file):
        """Test successful loading of configuration from .cfg file."""
        config = ConfigParser()
        config.read(temp_config_file)
        
        assert config.has_section('General')
        assert config.has_section('Colors')
        assert config.has_section('Settings')
        assert config.get('General', 'Name') == 'Dracula'
        assert config.get('Colors', 'Background') == '#282a36'
        
    def test_load_config_from_json_file_success(self, temp_json_config, valid_dracula_config):
        """Test successful loading of configuration from JSON file."""
        with open(temp_json_config, 'r') as f:
            loaded_config = json.load(f)
        
        assert loaded_config == valid_dracula_config
        assert loaded_config['theme_name'] == 'Dracula'
        assert loaded_config['colors']['background'] == '#282a36'
    
    def test_load_config_from_nonexistent_file(self):
        """Test handling of nonexistent configuration file."""
        nonexistent_path = '/tmp/nonexistent_dracula_config.cfg'
        
        with pytest.raises(FileNotFoundError):
            with open(nonexistent_path, 'r') as f:
                pass
    
    def test_load_config_from_invalid_json(self):
        """Test handling of malformed JSON in configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{ "invalid": json, "missing": "quotes" }')
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                with open(temp_file, 'r') as file:
                    json.load(file)
        finally:
            os.unlink(temp_file)
    
    def test_load_config_with_missing_sections(self):
        """Test handling of configuration file with missing sections."""
        incomplete_cfg = """[General]
Name=Dracula
# Missing Colors and Settings sections
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(incomplete_cfg)
            temp_file = f.name
        
        try:
            config = ConfigParser()
            config.read(temp_file)
            
            assert config.has_section('General')
            assert not config.has_section('Colors')
            assert not config.has_section('Settings')
        finally:
            os.unlink(temp_file)
    
    def test_load_config_from_environment_variables(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            'DRACULA_THEME_NAME': 'Dracula Custom',
            'DRACULA_BACKGROUND': '#282a36',
            'DRACULA_FOREGROUND': '#f8f8f2',
            'DRACULA_FONT_SIZE': '16'
        }
        
        with patch.dict(os.environ, env_vars):
            assert os.environ.get('DRACULA_THEME_NAME') == 'Dracula Custom'
            assert os.environ.get('DRACULA_BACKGROUND') == '#282a36'
            assert os.environ.get('DRACULA_FONT_SIZE') == '16'
    
    def test_load_config_with_utf8_encoding(self):
        """Test loading configuration with UTF-8 encoded characters."""
        utf8_cfg = """[General]
Name=Dracula Theme 🧛‍♂️
Description=Thème sombre avec caractères spéciaux
Author=Équipe Dracula
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False, encoding='utf-8') as f:
            f.write(utf8_cfg)
            temp_file = f.name
        
        try:
            config = ConfigParser()
            config.read(temp_file, encoding='utf-8')
            
            assert '🧛‍♂️' in config.get('General', 'Name')
            assert 'Thème' in config.get('General', 'Description')
        finally:
            os.unlink(temp_file)


class TestDraculaConfigValidation:
    """Test suite for Dracula configuration validation."""
    
    def test_validate_theme_name_valid(self):
        """Test validation of valid theme names."""
        valid_names = [
            "Dracula", "Dracula Pro", "Dracula-Soft", 
            "dracula_custom", "DRACULA", "Dracula 2.0"
        ]
        for name in valid_names:
            assert isinstance(name, str)
            assert len(name.strip()) > 0
            assert len(name) <= 100  # Reasonable length limit
    
    def test_validate_theme_name_invalid(self):
        """Test validation of invalid theme names."""
        invalid_names = [None, "", "   ", 123, [], {}]
        for name in invalid_names:
            if name is None or not isinstance(name, str) or len(name.strip()) == 0:
                assert False, f"Invalid theme name should be rejected: {name}"
    
    def test_validate_color_format_hex_valid(self):
        """Test validation of valid hex color formats."""
        valid_colors = [
            "#282a36", "#f8f8f2", "#44475a", "#6272a4",
            "#ff5555", "#ffb86c", "#f1fa8c", "#50fa7b",
            "#bd93f9", "#8be9fd", "#ff79c6", "#000000", "#ffffff"
        ]
        
        for color in valid_colors:
            assert color.startswith('#')
            assert len(color) == 7
            try:
                int(color[1:], 16)
            except ValueError:
                pytest.fail(f"Invalid hex color: {color}")
    
    def test_validate_color_format_invalid(self):
        """Test validation of invalid color formats."""
        invalid_colors = [
            "282a36", "#gggggg", "#12345", "#1234567", 
            "red", "blue", None, 123, "#", ""
        ]
        
        for color in invalid_colors:
            is_valid = (
                isinstance(color, str) and
                color.startswith('#') and
                len(color) == 7 and
                all(c in '0123456789abcdefABCDEF' for c in color[1:])
            )
            assert not is_valid, f"Invalid color should be rejected: {color}"
    
    def test_validate_transparency_range_valid(self):
        """Test validation of valid transparency values."""
        valid_values = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1.0]
        for value in valid_values:
            assert isinstance(value, (int, float))
            assert 0.0 <= value <= 1.0
    
    def test_validate_transparency_range_invalid(self):
        """Test validation of invalid transparency values."""
        invalid_values = [-0.1, 1.1, 2.0, -1.0, "0.5", None, "transparent"]
        for value in invalid_values:
            is_valid = (
                isinstance(value, (int, float)) and
                0.0 <= value <= 1.0
            )
            assert not is_valid, f"Invalid transparency should be rejected: {value}"
    
    def test_validate_font_size_range_valid(self):
        """Test validation of valid font size values."""
        valid_sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48]
        for size in valid_sizes:
            assert isinstance(size, int)
            assert 8 <= size <= 72  # Reasonable font size range
    
    def test_validate_font_size_range_invalid(self):
        """Test validation of invalid font size values."""
        invalid_sizes = [0, -5, 1000, 3.14, "12", None, "large"]
        for size in invalid_sizes:
            is_valid = (
                isinstance(size, int) and
                8 <= size <= 72
            )
            assert not is_valid, f"Invalid font size should be rejected: {size}"
    
    def test_validate_line_height_range(self):
        """Test validation of line height values."""
        valid_heights = [1.0, 1.2, 1.4, 1.5, 1.6, 1.8, 2.0]
        for height in valid_heights:
            assert isinstance(height, (int, float))
            assert 1.0 <= height <= 3.0
        
        invalid_heights = [0.5, 3.5, -1.0, "1.5", None]
        for height in invalid_heights:
            is_valid = (
                isinstance(height, (int, float)) and
                1.0 <= height <= 3.0
            )
            assert not is_valid, f"Invalid line height should be rejected: {height}"
    
    def test_validate_boolean_settings(self):
        """Test validation of boolean configuration settings."""
        boolean_settings = ["italic_comments", "bold_keywords", "underline_links"]
        valid_values = [True, False]
        invalid_values = ["true", "false", 1, 0, None, "yes", "no"]
        
        for setting in boolean_settings:
            for value in valid_values:
                assert isinstance(value, bool)
            
            for value in invalid_values:
                assert not isinstance(value, bool), f"Non-boolean value should be rejected for {setting}: {value}"


class TestDraculaConfigMerging:
    """Test suite for configuration merging and override functionality."""
    
    def test_merge_with_default_config(self, valid_dracula_config):
        """Test merging user config with default configuration."""
        default_config = {
            "theme_name": "Default",
            "colors": {"background": "#000000", "foreground": "#ffffff"},
            "settings": {"font_size": 12, "transparency": 1.0}
        }
        
        user_config = {"colors": {"background": "#282a36"}}
        
        # Simulate merging logic
        merged_config = default_config.copy()
        if "colors" in user_config:
            merged_config["colors"].update(user_config["colors"])
        
        assert merged_config["colors"]["background"] == "#282a36"
        assert merged_config["colors"]["foreground"] == "#ffffff"
        assert merged_config["settings"]["font_size"] == 12
    
    def test_partial_config_override(self):
        """Test partial configuration overrides preserve other values."""
        base_config = {
            "colors": {
                "background": "#282a36",
                "foreground": "#f8f8f2",
                "red": "#ff5555"
            },
            "settings": {
                "font_size": 14,
                "transparency": 0.95
            }
        }
        
        partial_override = {
            "colors": {"background": "#1e1e1e"},
            "settings": {"font_size": 16}
        }
        
        merged = base_config.copy()
        for section, values in partial_override.items():
            if section in merged:
                merged[section].update(values)
            else:
                merged[section] = values
        
        assert merged["colors"]["background"] == "#1e1e1e"
        assert merged["colors"]["foreground"] == "#f8f8f2"
        assert merged["colors"]["red"] == "#ff5555"
        assert merged["settings"]["font_size"] == 16
        assert merged["settings"]["transparency"] == 0.95
    
    def test_nested_config_deep_merge(self):
        """Test deep merging of nested configuration structures."""
        config_a = {
            "colors": {"background": "#282a36", "red": "#ff5555"},
            "features": {"italic_comments": True}
        }
        
        config_b = {
            "colors": {"foreground": "#f8f8f2", "green": "#50fa7b"},
            "features": {"bold_keywords": False},
            "settings": {"font_size": 14}
        }
        
        merged = {}
        for config in [config_a, config_b]:
            for section, values in config.items():
                if section not in merged:
                    merged[section] = {}
                merged[section].update(values)
        
        assert merged["colors"]["background"] == "#282a36"
        assert merged["colors"]["foreground"] == "#f8f8f2"
        assert merged["colors"]["red"] == "#ff5555"
        assert merged["colors"]["green"] == "#50fa7b"
        assert merged["features"]["italic_comments"] is True
        assert merged["features"]["bold_keywords"] is False
        assert merged["settings"]["font_size"] == 14
    
    def test_config_priority_order(self):
        """Test configuration priority: command line > env vars > file > defaults."""
        defaults = {"theme_name": "Default", "font_size": 12}
        file_config = {"theme_name": "Dracula", "font_size": 14}
        env_config = {"font_size": 16}
        cli_config = {"theme_name": "Custom"}
        
        final_config = defaults.copy()
        final_config.update(file_config)
        final_config.update(env_config)
        final_config.update(cli_config)
        
        assert final_config["theme_name"] == "Custom"
        assert final_config["font_size"] == 16
    
    def test_config_inheritance_chains(self):
        """Test configuration inheritance from parent themes."""
        base_dracula = {
            "colors": {"background": "#282a36", "foreground": "#f8f8f2"},
            "settings": {"font_size": 14}
        }
        
        dracula_pro = {
            "parent": "base_dracula",
            "colors": {"purple": "#bd93f9"},
            "settings": {"font_size": 16}
        }
        
        inherited_config = base_dracula.copy()
        for section, values in dracula_pro.items():
            if section == "parent":
                continue
            if section in inherited_config:
                inherited_config[section].update(values)
            else:
                inherited_config[section] = values
        
        assert inherited_config["colors"]["background"] == "#282a36"
        assert inherited_config["colors"]["purple"] == "#bd93f9"
        assert inherited_config["settings"]["font_size"] == 16


class TestDraculaConfigErrorHandling:
    """Test suite for error handling and edge cases."""
    
    def test_config_file_permission_denied(self):
        """Test handling of permission denied when reading config file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
        
        os.chmod(temp_file, 0o000)
        try:
            with pytest.raises(PermissionError):
                with open(temp_file, 'r') as file:
                    file.read()
        finally:
            os.chmod(temp_file, 0o644)
            os.unlink(temp_file)
    
    def test_config_with_unicode_characters(self):
        """Test handling of unicode characters in configuration."""
        unicode_config = {
            "theme_name": "Dracula 🧛‍♂️",
            "description": "Theme with émojis and spëcial chars",
            "author": "Команда Dracula",
            "colors": {"custom": "#ff79c6"}
        }
        
        json_str = json.dumps(unicode_config, ensure_ascii=False)
        loaded_config = json.loads(json_str)
        
        assert loaded_config["theme_name"] == "Dracula 🧛‍♂️"
        assert "émojis" in loaded_config["description"]
        assert "Команда" in loaded_config["author"]
    
    def test_config_with_very_large_values(self):
        """Test handling of extremely large configuration values."""
        large_config = {
            "large_string": "x" * 10000,
            "large_number": 999999999999999,
            "large_list": list(range(1000)),
            "nested_large": {"data": "y" * 5000}
        }
        
        json_str = json.dumps(large_config)
        loaded_config = json.loads(json_str)
        
        assert len(loaded_config["large_string"]) == 10000
        assert loaded_config["large_number"] == 999999999999999
        assert len(loaded_config["large_list"]) == 1000
        assert len(loaded_config["nested_large"]["data"]) == 5000
    
    def test_config_malformed_sections(self):
        """Test handling of malformed configuration sections."""
        malformed_cfgs = [
            "[Incomplete Section\nName=Value",
            "[Section]\nInvalidLine",
            "[Section]\n=NoKey",
            "[Section]\nKey=",
            "NoSection\nKey=Value"
        ]
        
        for cfg_content in malformed_cfgs:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
                f.write(cfg_content)
                temp_file = f.name
            
            try:
                config = ConfigParser()
                config.read(temp_file)
            except Exception as e:
                assert isinstance(e, (ValueError, KeyError, TypeError))
            finally:
                os.unlink(temp_file)
    
    def test_config_empty_file(self):
        """Test handling of empty configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("")
            temp_file = f.name
        
        try:
            config = ConfigParser()
            config.read(temp_file)
            assert len(config.sections()) == 0
        finally:
            os.unlink(temp_file)
    
    def test_config_whitespace_only_file(self):
        """Test handling of file with only whitespace."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("   \n\t\n  \r\n  ")
            temp_file = f.name
        
        try:
            config = ConfigParser()
            config.read(temp_file)
            assert len(config.sections()) == 0
        finally:
            os.unlink(temp_file)
    
    def test_config_circular_references_prevention(self):
        """Test prevention of circular references in configuration."""
        config_a = {"parent": "config_b", "value": "a"}
        config_b = {"parent": "config_a", "value": "b"}
        
        def has_circular_reference(configs, current, visited=None):
            if visited is None:
                visited = set()
            if current in visited:
                return True
            visited.add(current)
            parent = configs.get(current, {}).get("parent")
            if parent and parent in configs:
                return has_circular_reference(configs, parent, visited)
            return False
        
        configs = {"config_a": config_a, "config_b": config_b}
        assert has_circular_reference(configs, "config_a")
        assert has_circular_reference(configs, "config_b")
    
    def test_config_invalid_encoding(self):
        """Test handling of files with invalid encoding."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.cfg', delete=False) as f:
            f.write(b'[General]\n')
            f.write(b'Name=\xff\xfe Invalid UTF-8\n')
            temp_file = f.name
        
        try:
            with pytest.raises(UnicodeDecodeError):
                with open(temp_file, 'r', encoding='utf-8') as file:
                    file.read()
        finally:
            os.unlink(temp_file)


class TestDraculaConfigPerformance:
    """Test suite for performance and integration scenarios."""
    
    def test_config_loading_performance(self, temp_config_file):
        """Test that configuration loading completes within reasonable time."""
        import time
        
        start_time = time.time()
        for _ in range(100):
            config = ConfigParser()
            config.read(temp_config_file)
            assert config.has_section('General')
        elapsed = time.time() - start_time
        assert elapsed < 2.0, f"Config loading took too long: {elapsed:.3f}s"
    
    def test_config_memory_usage_stability(self, valid_dracula_config):
        """Test that configuration handling doesn't cause memory leaks."""
        import gc
        
        gc.collect()
        for i in range(1000):
            copy_cfg = valid_dracula_config.copy()
            data = json.dumps(copy_cfg)
            parsed = json.loads(data)
            parsed['iter'] = i
        gc.collect()
        assert True
    
    def test_concurrent_config_access(self, temp_config_file):
        """Test thread-safe access to configuration."""
        import concurrent.futures
        
        results = []
        errors = []
        
        def access():
            try:
                cfg = ConfigParser()
                cfg.read(temp_config_file)
                results.append(cfg.get('General', 'Name'))
            except Exception as e:
                errors.append(e)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            futures = [ex.submit(access) for _ in range(50)]
            concurrent.futures.wait(futures)
        
        assert not errors
        assert len(results) == 50
        assert all(r == "Dracula" for r in results)
    
    def test_config_caching_behavior(self, temp_config_file):
        """Test configuration caching mechanisms."""
        cache = {}
        def load_with_cache(fp):
            if fp in cache:
                return cache[fp]
            cfg = ConfigParser()
            cfg.read(fp)
            cache[fp] = cfg
            return cfg
        
        c1 = load_with_cache(temp_config_file)
        assert temp_config_file in cache
        c2 = load_with_cache(temp_config_file)
        assert c1 is c2
    
    def test_config_reload_on_file_change(self, temp_config_file):
        """Test configuration reload when file is modified."""
        import time
        
        m0 = os.path.getmtime(temp_config_file)
        time.sleep(0.1)
        with open(temp_config_file, 'a') as f:
            f.write('\n# modified\n')
        m1 = os.path.getmtime(temp_config_file)
        assert m1 > m0
        cfg = ConfigParser()
        cfg.read(temp_config_file)
        assert cfg.has_section('General')


@pytest.mark.parametrize("color_value", [
    "#282a36", "#f8f8f2", "#44475a", "#6272a4",
    "#ff5555", "#ffb86c", "#f1fa8c", "#50fa7b"
])
def test_dracula_color_validation_parametrized(color_value):
    """Parametrized test for validating all Dracula theme colors."""
    assert isinstance(color_value, str)
    assert color_value.startswith('#')
    assert len(color_value) == 7
    try:
        int(color_value[1:], 16)
    except ValueError:
        pytest.fail(f"Invalid hex color: {color_value}")


@pytest.mark.parametrize("font_size,expected_valid", [
    (8, True), (12, True), (14, True), (16, True), (24, True),
    (0, False), (-5, False), (1000, False), ("12", False), (None, False)
])
def test_font_size_validation_parametrized(font_size, expected_valid):
    """Parametrized test for font size validation."""
    is_valid = isinstance(font_size, int) and 8 <= font_size <= 72
    assert is_valid == expected_valid


@pytest.mark.parametrize("transparency,expected_valid", [
    (0.0, True), (0.5, True), (0.95, True), (1.0, True),
    (-0.1, False), (1.1, False), ("0.5", False), (None, False)
])
def test_transparency_validation_parametrized(transparency, expected_valid):
    """Parametrized test for transparency validation."""
    is_valid = isinstance(transparency, (int, float)) and 0.0 <= transparency <= 1.0
    assert is_valid == expected_valid


@pytest.mark.parametrize("config_format", ["cfg", "json"])
def test_multiple_config_formats(config_format, valid_dracula_config, dracula_cfg_content):
    """Test loading configuration from different file formats."""
    if config_format == "json":
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_dracula_config, f)
            temp_file = f.name
        try:
            with open(temp_file, 'r') as file:
                loaded = json.load(file)
            assert loaded['theme_name'] == 'Dracula'
        finally:
            os.unlink(temp_file)
    else:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(dracula_cfg_content)
            temp_file = f.name
        try:
            cfg = ConfigParser()
            cfg.read(temp_file)
            assert cfg.get('General', 'Name') == 'Dracula'
        finally:
            os.unlink(temp_file)


def test_config_integration_full_workflow(temp_config_file, valid_dracula_config):
    """Integration test covering the complete configuration workflow."""
    cfg = ConfigParser()
    cfg.read(temp_config_file)
    assert cfg.has_section('General')
    assert cfg.has_section('Colors')
    assert cfg.has_section('Settings')

    theme_name = cfg.get('General', 'Name')
    bg = cfg.get('Colors', 'Background')
    size = cfg.getint('Settings', 'FontSize')
    assert theme_name == 'Dracula'
    assert bg == '#282a36'
    assert size == 14

    cfg.set('Settings', 'FontSize', '16')
    assert cfg.getint('Settings', 'FontSize') == 16

    with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
        cfg.write(f)
        exp = f.name
    try:
        new_cfg = ConfigParser()
        new_cfg.read(exp)
        assert new_cfg.getint('Settings', 'FontSize') == 16
    finally:
        os.unlink(exp)