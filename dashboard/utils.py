

def macro_expand(text, **substitutions):
    for key, substitution in substitutions.items():
        text_marker = '{' + key + '}'
        while text_marker in text:
            text = text.replace(text_marker,
                    macro_expand(substitution, **substitutions))
    return text

