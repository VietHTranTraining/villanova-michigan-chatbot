ENV_CONFIG = {
    "name": "mm-config",
    "description": "configuration for March Madness articles",
    "workflow": {
      "conversions": {
        "word": {
          "heading": {
            "fonts": [
              {
                "level": 1,
                "min_size": 24,
                "bold": False,
                "italic": False
              },
              {
                "level": 2,
                "min_size": 18,
                "max_size": 23,
                "bold": True,
                "italic": False
              },
              {
                "level": 3,
                "min_size": 14,
                "max_size": 17,
                "bold": False,
                "italic": False
              },
              {
                "level": 4,
                "min_size": 13,
                "max_size": 13,
                "bold": True,
                "italic": False
              }
            ],
            "styles": [
              {
                "level": 1,
                "names": [
                  "pullout heading",
                  "pulloutheading",
                  "header"
                ]
              },
              {
                "level": 2,
                "names": [
                  "subtitle"
                ]
              }
            ]
          }
        },
        "html": {
          "exclude_tags_completely": [
            "script",
            "sup",
            "link",
            "meta",
            "canvas",
            "svg"
          ],
          "exclude_tags_keep_content": [
            "font",
            "em",
            "span"
          ],
          "exclude_content": {
            "xpaths": []
          },
          "keep_content": {
            "xpaths": []
          },
          "exclude_tag_attributes": [
            "EVENT_ACTIONS"
          ]
        },
        "json_normalizations": []
      },
      "enrichments": [
        {
          "source_field": "text",
          "destination_field": "enriched_text",
          "enrichment": "natural_language_understanding",
          "options": {
            "features": {
              "entities": {
                "sentiment": True,
                "emotion": False,
                "limit": 50
              },
              "sentiment": {
                "document": True
              },
              "categories": {},
              "concepts": {
                "limit": 8
              },
              "keywords": {}
            }
          }
        }
      ],
      "normalizations": []
    },
    "environment_id": None
}
