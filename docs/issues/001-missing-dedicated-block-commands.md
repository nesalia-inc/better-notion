# Missing Dedicated Block Commands

## Description
The CLI provides dedicated commands for some block types (e.g., `heading`, `paragraph`, `code`, `todo`) but not for others. Users must use the generic `create` command for:
- Bullet lists (`bulleted_list_item`)
- Numbered lists (`numbered_list_item`)
- Quotes (`quote`)
- Callouts (`callout`)

## Current Behavior
Users need to use:
```bash
notion blocks create --parent <id> --type bullet --content "Item text"
notion blocks create --parent <id> --type numbered --content "Item text"
notion blocks create --parent <id> --type quote --content "Quote text"
notion blocks create --parent <id> --type callout --content "Callout text"
```

## Expected Behavior
Should have dedicated commands for consistency:
```bash
notion blocks bullet --parent <id> --text "Item text"
notion blocks numbered --parent <id> --text "Item text"
notion blocks quote --parent <id> --text "Quote text"
notion blocks callout --parent <id> --text "Callout text"
```

## Impact
- **Inconsistency**: Some block types have dedicated commands, others don't
- **Discoverability**: Users may not realize these block types are available
- **User Experience**: Requires looking up generic `create` command syntax

## Workaround
Use the generic `notion blocks create` command with `--type` parameter.

## Example Comparison
Current CLI:
```bash
# Has dedicated command ✅
notion blocks heading --parent <id> --text "Title" --level 1

# No dedicated command ❌
notion blocks create --parent <id> --type bullet --content "Item"
```

Proposed CLI:
```bash
# Both have dedicated commands ✅
notion blocks heading --parent <id> --text "Title" --level 1
notion blocks bullet --parent <id> --text "Item"
```

## Implementation Notes
The block models already support these types:
- `better_notion._sdk.models.blocks.Bullet`
- `better_notion._sdk.models.blocks.Numbered`
- `better_notion._sdk.models.blocks.Quote`
- `better_notion._sdk.models.blocks.Callout`

CLI commands can be added in `better_notion/_cli/commands/blocks.py` similar to existing commands like `create_heading`, `create_paragraph`, etc.

## Related
- Issue #002: Todo command --checked parameter bug
- Issue #003: notion blocks children command broken
