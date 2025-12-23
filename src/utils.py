def dump_ast(node, level=0):
    """
   
    """
    indent = "    " * level
    
    if isinstance(node, list):
        if not node:
            pass
        for item in node:
            dump_ast(item, level)
        return

    if not hasattr(node, "__dict__"): 
        print(f"{indent}{repr(node)}")
        return

    print(f"{indent}{type(node).__name__}")

    if hasattr(node, 'location'):
        print(f"{indent}  .location: {repr(getattr(node, 'location'))}")
    
    for key, value in vars(node).items():
        if key == 'location': 
           continue
            
        # pomijamy np brak else w ifie
        if value is None:
            continue
            
        print(f"{indent}  .{key}:", end="")
        
        if isinstance(value, (int, float, bool, str)):
            print(f" {repr(value)}")
        else:
           
            print() 
            dump_ast(value, level + 1)