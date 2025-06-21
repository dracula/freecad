import unittest
import os
import tempfile
import shutil
import time
import textwrap
import xml.etree.ElementTree as ET

from package_xml import parse_package_xml, parse_package_xml_file, validate_package_xml


class TestPackageXML(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_package_xml = os.path.join(self.temp_dir, "package.xml")

    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_parse_valid_package_xml_format2(self):
        """Test parsing a valid package.xml with format 2."""
        xml_content = textwrap.dedent("""\
            <?xml version="1.0"?>
            <package format="2">
                <name>test_package</name>
                <version>1.0.0</version>
                <description>Test package description</description>
                <maintainer email="test@example.com">Test Maintainer</maintainer>
                <license>MIT</license>
                <depend>rospy</depend>
                <build_depend>catkin</build_depend>
            </package>
        """)
        result = parse_package_xml(xml_content)
        self.assertEqual(result["format"], "2")
        self.assertEqual(result["name"], "test_package")
        self.assertEqual(result["version"], "1.0.0")
        self.assertEqual(result["description"], "Test package description")
        self.assertEqual(result["maintainers"][0]["name"], "Test Maintainer")
        self.assertEqual(result["maintainers"][0]["email"], "test@example.com")
        self.assertIn("MIT", result["licenses"])
        self.assertIn("rospy", result["dependencies"].get("depend", []))
        self.assertIn("catkin", result["dependencies"].get("build_depend", []))

    def test_parse_valid_package_xml_format3_with_optional_elements(self):
        """Test parsing a valid package.xml with format 3 and optional author."""
        xml_content = textwrap.dedent("""\
            <?xml version="1.0"?>
            <package format="3">
                <name>test_pkg3</name>
                <version>2.0.0</version>
                <description>Format 3 description</description>
                <maintainer email="maint@ex.com">Maintainer Name</maintainer>
                <license>BSD</license>
                <author email="auth@ex.com">Author Name</author>
                <depend>roscpp</depend>
                <build_depend>catkin</build_depend>
            </package>
        """)
        result = parse_package_xml(xml_content)
        self.assertEqual(result["format"], "3")
        self.assertEqual(result["authors"][0]["name"], "Author Name")
        self.assertEqual(result["authors"][0]["email"], "auth@ex.com")
        self.assertIn("BSD", result["licenses"])
        self.assertIn("roscpp", result["dependencies"].get("depend", []))

    def test_parse_multiple_dependencies_maintainers_and_licenses(self):
        """Test parsing package.xml with multiple maintainers, authors, licenses, and dependencies."""
        xml_content = textwrap.dedent("""\
            <?xml version="1.0"?>
            <package format="2">
                <name>multi_pkg</name>
                <version>1.2.3</version>
                <description>Multi elements</description>
                <maintainer email="m1@ex.com">M1</maintainer>
                <maintainer email="m2@ex.com">M2</maintainer>
                <author email="a1@ex.com">A1</author>
                <author email="a2@ex.com">A2</author>
                <license>Apache-2.0</license>
                <license>GPLv3</license>
                <depend>dep1</depend>
                <depend>dep2</depend>
            </package>
        """)
        result = parse_package_xml(xml_content)
        self.assertEqual(len(result["maintainers"]), 2)
        self.assertEqual(len(result["authors"]), 2)
        self.assertEqual(len(result["licenses"]), 2)
        self.assertListEqual(result["dependencies"].get("depend", []), ["dep1", "dep2"])

    def test_parse_invalid_xml_syntax(self):
        """Test handling of malformed XML syntax."""
        invalid_xml = textwrap.dedent("""\
            <?xml version="1.0"?>
            <package format="2">
                <name>test_package</name>
                <version>1.0.0</version>
                <description>Missing closing tag
                <maintainer email="test@example.com">Test Maintainer</maintainer>
            </package>
        """)
        with self.assertRaises(ET.ParseError):
            parse_package_xml(invalid_xml)

    def test_missing_required_elements(self):
        """Test parsing when required elements are missing."""
        base_fields = {
            "name": "<name>pkg</name>",
            "version": "<version>1.0.0</version>",
            "description": "<description>Desc</description>",
            "maintainer": '<maintainer email="e@ex.com">Name</maintainer>',
            "license": "<license>MIT</license>"
        }
        for missing in base_fields:
            with self.subTest(missing=missing):
                fields = [v for k, v in base_fields.items() if k != missing]
                xml = textwrap.dedent(f"""\
                    <?xml version="1.0"?>
                    <package format="2">
                        {''.join(fields)}
                    </package>
                """)
                with self.assertRaises(ValueError):
                    parse_package_xml(xml)

    def test_invalid_version_and_email_and_format(self):
        """Test invalid version formats, email formats, and unsupported package formats."""
        # Invalid version
        xml_bad_version = textwrap.dedent("""\
            <?xml version="1.0"?>
            <package format="2">
                <name>pkg</name><version>bad_version</version>
                <description>Desc</description>
                <maintainer email="e@ex.com">Name</maintainer>
                <license>MIT</license>
            </package>
        """)
        with self.assertRaises(ValueError):
            parse_package_xml(xml_bad_version)
        # Invalid email
        xml_bad_email = xml_bad_version.replace("bad_version", "1.0.0").replace("e@ex.com", "not-an-email")
        with self.assertRaises(ValueError):
            parse_package_xml(xml_bad_email)
        # Unsupported format
        xml_bad_format = xml_bad_version.replace('format="2"', 'format="4"').replace("bad_version", "1.0.0")
        with self.assertRaises(ValueError):
            parse_package_xml(xml_bad_format)

    def test_circular_dependencies(self):
        """Test detection of circular dependencies."""
        xml_circular = textwrap.dedent("""\
            <?xml version="1.0"?>
            <package format="2">
                <name>circular</name>
                <version>1.0.0</version>
                <description>Circular dep</description>
                <maintainer email="e@ex.com">Name</maintainer>
                <license>MIT</license>
                <depend>circular</depend>
            </package>
        """)
        with self.assertRaises(ValueError):
            parse_package_xml(xml_circular)

    def test_edge_cases_long_and_empty_and_whitespace(self):
        """Test long content, empty files, and whitespace-only files."""
        # Long content
        long_name = "n" * 1000
        long_version = "1." + "0" * 500
        long_desc = "d" * 2000
        xml_long = textwrap.dedent(f"""\
            <?xml version="1.0"?>
            <package format="2">
                <name>{long_name}</name>
                <version>{long_version}</version>
                <description>{long_desc}</description>
                <maintainer email="e@ex.com">Name</maintainer>
                <license>MIT</license>
            </package>
        """)
        result = parse_package_xml(xml_long)
        self.assertEqual(result["name"], long_name)
        self.assertEqual(result["version"], long_version)
        self.assertEqual(result["description"], long_desc)
        # Empty and whitespace-only
        with self.assertRaises(ET.ParseError):
            parse_package_xml("")
        with self.assertRaises(ET.ParseError):
            parse_package_xml("   \n   ")

    def test_unicode_and_large_dependency_list(self):
        """Test parsing unicode content and large number of dependencies."""
        xml_unicode = textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <package format="2">
                <name>测试包_ü</name>
                <version>1.0.0</version>
                <description>测试包描述 with émojis 🚀</description>
                <maintainer email="t@ex.com">Тест</maintainer>
                <license>MIT</license>
            </package>
        """)
        result_unicode = parse_package_xml(xml_unicode)
        self.assertIn("测试包_ü", result_unicode["name"])
        self.assertIn("émojis 🚀", result_unicode["description"])
        # Large dependency list
        deps = "\n".join([f"    <depend>pkg{i}</depend>" for i in range(1000)])
        xml_large = textwrap.dedent(f"""\
            <?xml version="1.0"?>
            <package format="2">
                <name>large</name>
                <version>1.0.0</version>
                <description>Large deps</description>
                <maintainer email="e@ex.com">Name</maintainer>
                <license>MIT</license>
            {deps}
            </package>
        """)
        result_large = parse_package_xml(xml_large)
        self.assertEqual(len(result_large["dependencies"].get("depend", [])), 1000)

    def test_validate_dependency_types(self):
        """Test validation of different dependency types."""
        xml_content = textwrap.dedent("""\
            <?xml version="1.0"?>
            <package format="2">
                <name>dep_types</name>
                <version>1.0.0</version>
                <description>Test deps</description>
                <maintainer email="e@ex.com">Name</maintainer>
                <license>MIT</license>
                <build_depend>catkin</build_depend>
                <exec_depend>rospy</exec_depend>
                <test_depend>rosunit</test_depend>
                <doc_depend>doxygen</doc_depend>
            </package>
        """)
        parsed = parse_package_xml(xml_content)
        validated = validate_package_xml(parsed)
        self.assertEqual(validated["dependencies"].get("build_depend"), ["catkin"])
        self.assertEqual(validated["dependencies"].get("exec_depend"), ["rospy"])

    def test_file_io_operations(self):
        """Test reading from file, non-existent files, and permission errors."""
        xml_content = textwrap.dedent("""\
            <?xml version="1.0"?>
            <package format="2">
                <name>file_io</name>
                <version>1.0.0</version>
                <description>IO test</description>
                <maintainer email="e@ex.com">Name</maintainer>
                <license>MIT</license>
            </package>
        """)
        # Write and read
        with open(self.test_package_xml, "w", encoding="utf-8") as f:
            f.write(xml_content)
        result = parse_package_xml_file(self.test_package_xml)
        self.assertEqual(result["name"], "file_io")
        # Non-existent
        with self.assertRaises(FileNotFoundError):
            parse_package_xml_file(os.path.join(self.temp_dir, "no.xml"))
        # Permission denied
        os.chmod(self.test_package_xml, 0)
        with self.assertRaises(PermissionError):
            parse_package_xml_file(self.test_package_xml)
        os.chmod(self.test_package_xml, 0o644)

    def test_parse_large_package_xml_performance(self):
        """Test parsing performance for large package.xml."""
        deps = "\n".join([f"    <depend>pkg{i}</depend>" for i in range(5000)])
        xml_content = textwrap.dedent(f"""\
            <?xml version="1.0"?>
            <package format="2">
                <name>perf</name>
                <version>1.0.0</version>
                <description>Performance test</description>
                <maintainer email="e@ex.com">Name</maintainer>
                <license>MIT</license>
            {deps}
            </package>
        """)
        start = time.perf_counter()
        result = parse_package_xml(xml_content)
        duration = time.perf_counter() - start
        self.assertTrue(duration < 1.0, f"Parsing took too long: {duration}s")
        self.assertEqual(len(result["dependencies"].get("depend", [])), 5000)


if __name__ == "__main__":
    unittest.main()