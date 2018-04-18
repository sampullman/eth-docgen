from yattag import Doc
import json
import re
from cgi import escape

def deconstruct_pragma(pragma):
    if pragma[0] == 'solidity':
        version = ''.join(pragma[2:])
        if pragma[1] == '^':
            return [pragma[0], 'Solidity version must be greater than {}'.format(version)]

def make_js(line, abi, source, bytecode):
    line('script', """
        function copyToClipboard(text) {{
            var textArea = document.getElementById('__doc_copy');
            if(!textArea) {{
                textArea = document.createElement("textarea");
                textArea.setAttribute('id', '__doc_copy');
            document.body.appendChild(textArea);
            }}
            textArea.value = text;
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
        }}
        function copyOnClick(text) {{ return function() {{ copyToClipboard(text); }}}}
        window.onload = function() {{
            document.getElementById("copy_abi").onclick = copyOnClick('{abi}');
            //document.getElementById("copy_source").onclick = copyOnClick('{source}');
            document.getElementById("copy_bytecode").onclick = copyOnClick('{bytecode}');
        }}
    """.format(abi=abi, source=json.dumps(source), bytecode=escape(bytecode)))

def make_overview(tag, line, contract_doc, base_contracts, pragmas):
    with tag('div', id="contract_info"):
        section_title(line, 'Contract Overview')

        contract_doc = [line.strip() for line in contract_doc.split('\n')]
        authors = []
        for doc_line in contract_doc:
            if doc_line.startswith('@author'):
                authors.append(doc_line[7:])
        if len(authors) > 0:
            if len(authors) == 1:
                authors_text = authors[0]
            else:
                authors_text = ', '.join(authors[:-1]) + ' and ' + authors[-1]
            line('div', 'Authored by {}'.format(authors_text))
        if len(base_contracts) > 0:
            line('div', 'Inherits from {}'.format(', '.join(base_contracts)), klass='inherit')
        line('h4', 'Click to copy data')
        line('textarea', '', id='__doc_copy')
        with tag('div', klass='copy_data'):
            line('div', 'ABI', id='copy_abi')
            line('div', 'Source', id='copy_source')
            line('div', 'Bytecode', id='copy_bytecode')

        if len(pragmas) > 0:
            def display_fn(tag, line, item):
                line('td', item[0], klass='pragma_name center')
                line('td', item[1], klass='info')
            pragma_data = [deconstruct_pragma(pragma) for pragma in pragmas]
            section(tag, line, 'pragmas', 'Pragmas', pragma_data, display_fn)

def section_title(line, name):
    line('h2', name)
    line('hr', '')

def section(tag, line, id, title, data, display_fn):

    with tag('table', id=id, klass="section"):
        if title:
            with tag('tr'):
                line('th', title, colspan='2')
        for item in data:
            with tag('tr'):
                display_fn(tag, line, item)

def full_type(type_node):
    return type_node['typeDescriptions']['typeString'].split()[0]

# variable is an AST node that represents a state variable
def type_name(name_node, full=False):
    
    if name_node['nodeType'] == 'ArrayTypeName':
        if full:
            return full_type(name_node)
        return name_node['baseType']['name']+'[]'

    if name_node['nodeType'] == 'Mapping':
        key_name = type_name(name_node['keyType'])
        value_name = type_name(name_node['valueType'])
        return "mapping({} => {})".format(key_name, value_name)
    else:
        if full:
            return full_type(name_node)
        return name_node['name']

def base_var_type(var_type):
    if var_type.startswith('mapping'):
        return 'mapping'
    bracket = var_type.find('[')
    if bracket != -1:
        return var_type[:bracket]
    return var_type
def glean_comments(source_lines, index):
    comments = {'notice': []}
    while True:
        if index <= 0:
            return comments
            print('Something weird happened, comment was first source line?')
        c = source_lines[index].strip()
        if c.startswith('///'):
            c = c[3:].strip()
            if c.startswith('@param'):
                words = c.split()
                if len(words) > 1:
                    comments[words[1]] = ' '.join(words[2:])
            else:
                if c.startswith('@notice'):
                    c = c[7:].strip()
                comments['notice'].append(c)
        else:
            return comments
        index -= 1

def generic_comments(source_lines, regex):
    matcher = re.compile(regex)
    for i, line in enumerate(source_lines):
        if matcher.search(line):
            return glean_comments(source_lines, i-1)
    return {'notice': []}

def event_comments(source_lines, name):
    return generic_comments(source_lines, r'event\s+?{}\(.*?\);'.format(name))

def struct_comments(source_lines, name):
    return generic_comments(source_lines, r'struct\s+?{}\s*?{{'.format(name))

def var_comments(source_lines, name, var_type):
    var_type = base_var_type(var_type)
    regex = r'.*?{}[ \[\]()=>a-zA-Z]*?\s*?{}\s*?(=.*?)?;.*?'.format(var_type, name)
    return generic_comments(source_lines, regex)

def custom_display_fn(source_lines, showVisibility=False, comment_fn=var_comments):
    cols = '1' if showVisibility else '2'
    def display_fn(tag, line, item):
        tname = type_name(item['typeName'])
        name = item['name']
        desc = '<br />'.join(comment_fn(source_lines, name, tname)['notice'])

        if showVisibility:
            line('td', item['visibility'], klass="visibility center")
        with tag('td', klass="info", colspan=cols):
            line('span', name, klass='name')
            line('span', tname, klass='type')
            if desc:
                line('div', desc, klass='description')
    return display_fn

def make_variables(tag, line, contract, source_lines):
    state = filter(lambda x: x['nodeType']=='VariableDeclaration', contract)
    section_title(line, 'State Variables')
    display_fn = custom_display_fn(source_lines, showVisibility=True)
    section(tag, line, 'state_vars', None, state, display_fn)

def make_structs(tag, line, contract, source_lines):
    state = filter(lambda x: x['nodeType']=='StructDefinition', contract)

    section_title(line, 'Structs')
    for struct in state:
        display_fn = custom_display_fn(source_lines)
        name = struct['name']
        line('h3', name)
        comments = struct_comments(source_lines, name)
        if comments['notice']:
            line('div', '<br />'.join(comments['notice']), klass='function_desc')
        section(tag, line, 'structs', 'Fields', struct['members'], display_fn)

def make_events(tag, line, contract, source_lines):
    state = filter(lambda x: x['nodeType']=='EventDefinition', contract)

    section_title(line, 'Events')
    for event in state:
        display_fn = custom_display_fn(source_lines)
        name = event['name']
        line('h3', name)
        comments = event_comments(source_lines, name)
        if comments['notice']:
            line('div', '<br />'.join(comments['notice']), klass='function_desc')
        section(tag, line, 'events', 'Parameters', event['parameters']['parameters'], display_fn)

def userdoc_notice(meta_doc, fn_sig):
    methods = meta_doc['userdoc']['methods']
    if fn_sig in methods:
        fn_doc = methods[fn_sig]
        if 'notice' in fn_doc:
            return fn_doc['notice']
    return ''

def devdoc_param(meta_doc, fn_sig, param):
    methods = meta_doc['devdoc']['methods']
    if fn_sig in methods and 'params' in methods[fn_sig]:
        param_doc = methods[fn_sig]['params']
        if param in param_doc:
            return param_doc[param]
    return ''

def abi_signature(function):
    params = ','.join(type_name(n, full=True) for n in function['parameters']['parameters'])
    return "{}({})".format(function['name'], params)

def var_list(param_node):
    return [(type_name(n['typeName']), n['name']) for n in param_node]

def fn_signature(tag, line, text, function):
    text(function['name']+'(')
    var_decls = var_list(function['parameters']['parameters'])
    for i, var_decl in enumerate(var_decls):
        line('span', var_decl[0], klass='type')
        text(' ')
        line('span', var_decl[1], klass='name')
        if i != len(var_decls) - 1:
            text(', ')
    text(') ')
            
    line('span', function['visibility'], klass='visibility')
    if function['stateMutability'] != 'nonpayable':
        line('span', ' '+function['stateMutability'], klass='mutability')
    
    returns = var_list(function['returnParameters']['parameters'])
    if len(returns) != 0:
        text(' ')
    for i, ret in enumerate(returns):
        line('span', ret[0], klass='type')
        line('span', ' '+ret[1], klass='name')
        if i != len(returns) - 1:
            text(', ')

def make_functions(tag, line, text, contract, meta_doc, source_lines):
    state = filter(lambda x: x['nodeType']=='FunctionDefinition', contract)

    section_title(line, 'Functions')
    for function in state:
        if function['name'] == '':
            line('h3', 'Fallback function')
        else:
            line('h3', function['name'])

        with tag('div', klass="function_sig"):
            fn_signature(tag, line, text, function)

        signature = abi_signature(function)
        line('div', userdoc_notice(meta_doc, signature), klass='function_desc')

        def display_fn(tag, line, item):
            tname = type_name(item['typeName'])
            name = item['name']
            desc = devdoc_param(meta_doc, signature, name)
            with tag('td', klass="info", colspan='2'):
                line('span', name, klass='name')
                line('span', tname, klass='type')
                if desc:
                    line('div', desc, klass='description')

        params = function['parameters']['parameters']
        if len(params) > 0:
            section(tag, line, 'parameters', 'Parameters', params, display_fn)
        returns = function['returnParameters']['parameters']
        if len(returns) > 0:
            section(tag, line, 'returns', 'Returns', returns, display_fn)

# Generate solidity html docs from metadata file
#   produced using: solc --metadata ... 
def docgen(abi_file, meta_file, out_file):

    with open(abi_file, 'r') as f:
        abi = json.load(f)
    pragmas = []
    for node in abi['ast']['nodes']:
        if node['nodeType'] == 'PragmaDirective':
            pragmas.append(node['literals'])
        elif node['nodeType'] == 'ContractDefinition':
            contract = node['nodes']
            base_contracts = [n['baseName']['name'] for n in node['baseContracts']]
            name = node['name']
            contract_doc = node['documentation']


    with open(meta_file, 'r') as f:
        metadata = json.load(f)
        meta_doc = metadata['output']
    
    print('Compiler version: {}'.format(metadata['compiler']['version']))
    source_lines = abi['source'].split('\n')

    with open(out_file, 'w') as f:
        doc, tag, text, line = Doc().ttl()
        make_js(line, json.dumps(abi['abi']), abi['source'], abi['bytecode'])
        line('h1', '{} Contract Documentation'.format(name))
        devdoc = meta_doc['devdoc']
        if 'title' in devdoc:
            line('div', devdoc['title'], klass='title_desc')

        make_overview(tag, line, contract_doc, base_contracts, pragmas)

        make_variables(tag, line, contract, source_lines)
        make_structs(tag, line, contract, source_lines)
        make_events(tag, line, contract, source_lines)
        make_functions(tag, line, text, contract, meta_doc, source_lines)

        with tag('div', id='footer'):
            line('hr', '')
            line('div', 'Contract documentation generated with eth-docgen')

        f.write(doc.getvalue())


if __name__ == '__main__':
    contract_abi = './build/contracts/TreasureHunt.json'
    contract_metadata = './build/contracts/TreasureHunt/TreasureHunt_meta.json'
    ouptut_file = '../website/home/templates/TreasureHunt.html'
    docgen(contract_abi, contract_metadata, ouptut_file)