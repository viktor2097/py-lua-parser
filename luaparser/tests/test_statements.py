from luaparser.utils  import tests
from luaparser import ast
from luaparser.astnodes import *
import textwrap


class StatementsTestCase(tests.TestCase):
    """
    3.3.1 – Blocks
    """
    def test_empty_block(self):
        tree = ast.parse(";;;;")
        exp = Chunk(body=Block(body=[]))
        self.assertEqual(exp, tree)

    def test_2_block(self):
        tree = ast.parse("local a;local b;")
        exp = Chunk(body=Block(body=[
            LocalAssign(targets=[Name('a')],values=[]),
            LocalAssign(targets=[Name('b')],values=[])
        ]))
        self.assertEqual(exp, tree)

        """
    3.3.3 – Assignment
    """
    def test_set_number(self):
        tree = ast.parse("i=3")
        exp = Chunk(body=Block(body=[
            Assign(targets=[Name('i')],values=[Number(3)])
        ]))
        self.assertEqual(exp, tree)

    def test_set_string(self):
        tree = ast.parse('i="foo bar"')
        exp = Chunk(body=Block(body=[
            Assign(targets=[Name('i')],values=[String('foo bar')])
        ]))
        self.assertEqual(exp, tree)

    def test_set_array_index(self):
        tree = ast.parse('a[i] = 42')
        exp = Chunk(body=Block(body=[
            Assign(targets=[Index(idx=Name('i'), value=Name('a'))], values=[Number(42)])
        ]))
        self.assertEqual(exp, tree)

    def test_set_table_index(self):
        tree = ast.parse('_ENV.x = val')
        exp = Chunk(body=Block(body=[
            Assign(targets=[Index(idx=Name('x'), value=Name('_ENV'))], values=[Name('val')])
        ]))
        self.assertEqual(exp, tree)

    def test_set_multi(self):
        tree = ast.parse('x, y = y, x')
        exp = Chunk(body=Block(body=[
            Assign(targets=[Name('x'), Name('y')],values=[Name('y'), Name('x')])
        ]))
        self.assertEqual(exp, tree)

    '''
    3.3.4 – Control Structures
    '''
    def test_for_in_1(self):
        tree = ast.parse(textwrap.dedent("""
            for k, v in pairs({}) do
              print(k, v)
            end
            """))
        exp = Chunk(body=Block(body=[
            Forin(
                body=[Call(func=Name('print'), args=[Name('k'), Name('v')])],
                iter=Call(func=Name('pairs'), args=[Table(keys=[], values=[])]),
                targets=[Name('k'), Name('v')]
            )
        ]))
        self.assertEqual(exp, tree)

        # test tokens
        nodes = list(ast.walk(tree))

        self.assertIsInstance(nodes[2], Forin)
        self.assertEqual(nodes[2].tokens[0].text, 'for')
        self.assertEqual(nodes[2].tokens[1].text, ' ')
        self.assertEqual(nodes[2].tokens[2].text, 'k')
        self.assertEqual(nodes[2].tokens[3].text, ',')
        self.assertEqual(nodes[2].tokens[4].text, ' ')
        self.assertEqual(nodes[2].tokens[5].text, 'v')
        self.assertEqual(nodes[2].tokens[6].text, ' ')
        self.assertEqual(nodes[2].tokens[7].text, 'in')
        self.assertEqual(nodes[2].tokens[8].text, ' ')
        self.assertEqual(nodes[2].tokens[9].text, 'pairs')
        self.assertEqual(nodes[2].tokens[10].text, '(')
        self.assertEqual(nodes[2].tokens[11].text, '{')
        self.assertEqual(nodes[2].tokens[12].text, '}')
        self.assertEqual(nodes[2].tokens[13].text, ')')
        self.assertEqual(nodes[2].tokens[14].text, ' ')
        self.assertEqual(nodes[2].tokens[15].text, 'do')
        self.assertEqual(nodes[2].tokens[16].text, '\n')
        self.assertEqual(nodes[2].tokens[17].text, '  ')
        self.assertEqual(nodes[2].tokens[18].text, 'print')
        self.assertEqual(nodes[2].tokens[19].text, '(')
        self.assertEqual(nodes[2].tokens[20].text, 'k')
        self.assertEqual(nodes[2].tokens[21].text, ',')
        self.assertEqual(nodes[2].tokens[22].text, ' ')
        self.assertEqual(nodes[2].tokens[23].text, 'v')
        self.assertEqual(nodes[2].tokens[24].text, ')')
        self.assertEqual(nodes[2].tokens[25].text, '\n')
        self.assertEqual(nodes[2].tokens[26].text, 'end')

        self.assertIsInstance(nodes[5], Call)
        self.assertEqual(nodes[5].tokens[0].text, 'pairs')
        self.assertEqual(nodes[5].tokens[1].text, '(')
        self.assertEqual(nodes[5].tokens[2].text, '{')
        self.assertEqual(nodes[5].tokens[3].text, '}')
        self.assertEqual(nodes[5].tokens[4].text, ')')

        self.assertIsInstance(nodes[6], Table)
        self.assertEqual(nodes[6].tokens[0].text, '{')
        self.assertEqual(nodes[6].tokens[1].text, '}')

        self.assertIsInstance(nodes[8], Call)
        self.assertEqual(nodes[8].tokens[0].text, 'print')
        self.assertEqual(nodes[8].tokens[1].text, '(')
        self.assertEqual(nodes[8].tokens[2].text, 'k')
        self.assertEqual(nodes[8].tokens[3].text, ',')
        self.assertEqual(nodes[8].tokens[4].text, ' ')
        self.assertEqual(nodes[8].tokens[5].text, 'v')
        self.assertEqual(nodes[8].tokens[6].text, ')')

    def test_for_in_2(self):
        tree = ast.parse(textwrap.dedent("""
            for k, v in foo.pairs({}) do
              print(k, v)
            end
            """))
        exp = Chunk(body=Block(body=[
            Forin(
                body=[Call(func=Name('print'), args=[Name('k'), Name('v')])],
                iter=Call(func=Index(Name('pairs'), Name('foo')), args=[Table(keys=[], values=[])]),
                targets=[Name('k'), Name('v')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_for_in_3(self):
        tree = ast.parse(textwrap.dedent("""
            for k, v in foo:pairs({}) do
              print(k, v)
            end
            """))
        exp = Chunk(body=Block(body=[
            Forin(
                body=[Call(func=Name('print'), args=[Name('k'), Name('v')])],
                iter=Invoke(source=Name('foo'), func=Name('pairs'), args=[Table(keys=[], values=[])]),
                targets=[Name('k'), Name('v')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_for_in_4(self):
        tree = ast.parse(textwrap.dedent("""
            for k, v in bar.foo:pairs({}) do
              print(k, v)
            end
            """))
        exp = Chunk(body=Block(body=[
            Forin(
                body=[Call(func=Name('print'), args=[Name('k'), Name('v')])],
                iter=Invoke(source=Index(Name('foo'), Name('bar')), func=Name('pairs'), args=[Table(keys=[], values=[])]),
                targets=[Name('k'), Name('v')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_for_in_5(self):
        tree = ast.parse(textwrap.dedent("""
            for k, v in bar:foo(42):pairs({}) do
              print(k, v)
            end
            """))
        exp = Chunk(body=Block(body=[
            Forin(
                body=[Call(func=Name('print'), args=[Name('k'), Name('v')])],
                iter=Invoke(
                    source=Invoke(source=Name('bar'), func=Name('foo'), args=[Number(42)]),
                    func=Name('pairs'),
                    args=[Table(keys=[], values=[])]),
                targets=[Name('k'), Name('v')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_for_in_6(self):
        tree = ast.parse(textwrap.dedent("""
            for k, v in bar:foo(42).pairs({}) do
              print(k, v)
            end
            """))
        exp = Chunk(body=Block(body=[
            Forin(
                body=[Call(func=Name('print'), args=[Name('k'), Name('v')])],
                iter=Call(
                    func=Index(idx=Name('pairs'), value=Invoke(source=Name('bar'), func=Name('foo'), args=[Number(42)])),
                    args=[Table(keys=[], values=[])]),
                targets=[Name('k'), Name('v')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_numeric_for(self):
        tree = ast.parse(textwrap.dedent("""
            for i=1,10,2 do print(i) end
            """))
        exp = Chunk(body=Block(body=[
            Fornum(
                target=Name('i'),
                start=Number(1),
                stop=Number(10),
                step=Number(2),
                body=[Call(func=Name('print'), args=[Name('i')])]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_do_end(self):
        tree = ast.parse(textwrap.dedent("""
            do
              local foo = 'bar'
            end
            """))
        exp = Chunk(body=Block(body=[
            Do(
                body=[LocalAssign(targets=[Name('foo')],values=[String('bar')])]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_while(self):
        tree = ast.parse(textwrap.dedent("""
            while true do
              print('hello world')
            end"""))
        exp = Chunk(body=Block(body=[
            While(test=TrueExpr(), body=[
                Call(func=Name('print'), args=[String('hello world')])
            ])
        ]))
        self.assertEqual(exp, tree)

    def test_repeat_until(self):
        tree = ast.parse(textwrap.dedent("""
            repeat        
            until true
            """))
        exp = Chunk(body=Block(body=[
            Repeat(body=[], test=TrueExpr())
        ]))
        self.assertEqual(exp, tree)

    def test_if(self):
        tree = ast.parse(textwrap.dedent("""
            if true then    
            end
            """))
        exp = Chunk(body=Block(body=[
            If(
                test=TrueExpr(),
                body=[],
                orelse=None
            )
        ]))
        self.assertEqual(exp, tree)

    def test_if_exp(self):
        tree = ast.parse(textwrap.dedent("""
            if (a<2) then    
            end
            """))
        exp = Chunk(body=Block(body=[
            If(
                test=LessThanOp(
                    left=Name('a'),
                    right=Number(2)
                ),
                body=[],
                orelse=None
            )
        ]))
        self.assertEqual(exp, tree)

    def test_if_elseif(self):
        tree = ast.parse(textwrap.dedent("""
            if true then 
            elseif false then     
            end
            """))
        exp = Chunk(body=Block(body=[
            If(
                test=TrueExpr(),
                body=[],
                orelse=ElseIf(test=FalseExpr(), body=[], orelse=None)
            )
        ]))
        self.assertEqual(exp, tree)

    def test_if_elseif_else(self):
        tree = ast.parse(textwrap.dedent("""
            if true then 
            elseif false then  
            else   
            end
            """))
        exp = Chunk(body=Block(body=[
            If(
                test=TrueExpr(),
                body=[],
                orelse=ElseIf(
                    test=FalseExpr(),
                    body=[],
                    orelse=[]
                )
            )
        ]))
        self.assertEqual(exp, tree)

    def test_if_elseif_elseif_else(self):
        tree = ast.parse(textwrap.dedent("""
            if true then
            elseif false then
            elseif 42 then
            else
              return true
            end
            """))
        exp = Chunk(body=Block(body=[
            If(
                test=TrueExpr(),
                body=[],
                orelse=ElseIf(
                    test=FalseExpr(),
                    body=[],
                    orelse=ElseIf(
                        test=Number(42),
                        body=[],
                        orelse=[Return([TrueExpr()])]
                    )
                )
            )
        ]))
        self.assertEqual(exp, tree)

        # test tokens
        nodes = list(ast.walk(tree))

        self.assertIsInstance(nodes[2], If)
        self.assertEqual(nodes[2].tokens[0].text, 'if')
        self.assertEqual(nodes[2].tokens[1].text, ' ')
        self.assertEqual(nodes[2].tokens[2].text, 'true')
        self.assertEqual(nodes[2].tokens[3].text, ' ')
        self.assertEqual(nodes[2].tokens[4].text, 'then')
        self.assertEqual(nodes[2].tokens[5].text, '\n')
        self.assertEqual(nodes[2].tokens[6].text, 'elseif')
        self.assertEqual(nodes[2].tokens[7].text, ' ')
        self.assertEqual(nodes[2].tokens[8].text, 'false')
        self.assertEqual(nodes[2].tokens[9].text, ' ')
        self.assertEqual(nodes[2].tokens[10].text, 'then')
        self.assertEqual(nodes[2].tokens[11].text, '\n')
        self.assertEqual(nodes[2].tokens[12].text, 'elseif')
        self.assertEqual(nodes[2].tokens[13].text, ' ')
        self.assertEqual(nodes[2].tokens[14].text, '42')
        self.assertEqual(nodes[2].tokens[15].text, ' ')
        self.assertEqual(nodes[2].tokens[16].text, 'then')
        self.assertEqual(nodes[2].tokens[17].text, '\n')
        self.assertEqual(nodes[2].tokens[18].text, 'else')
        self.assertEqual(nodes[2].tokens[19].text, '\n')
        self.assertEqual(nodes[2].tokens[20].text, '  ')
        self.assertEqual(nodes[2].tokens[21].text, 'return')
        self.assertEqual(nodes[2].tokens[22].text, ' ')
        self.assertEqual(nodes[2].tokens[23].text, 'true')
        self.assertEqual(nodes[2].tokens[24].text, '\n')
        self.assertEqual(nodes[2].tokens[25].text, 'end')

        self.assertIsInstance(nodes[3], ElseIf)
        self.assertEqual(nodes[3].tokens[0].text, 'elseif')
        self.assertEqual(nodes[3].tokens[1].text, ' ')
        self.assertEqual(nodes[3].tokens[2].text, 'false')
        self.assertEqual(nodes[3].tokens[3].text, ' ')
        self.assertEqual(nodes[3].tokens[4].text, 'then')

        self.assertIsInstance(nodes[4], ElseIf)
        self.assertEqual(nodes[4].tokens[0].text, 'elseif')
        self.assertEqual(nodes[4].tokens[1].text, ' ')
        self.assertEqual(nodes[4].tokens[2].text, '42')
        self.assertEqual(nodes[4].tokens[3].text, ' ')
        self.assertEqual(nodes[4].tokens[4].text, 'then')

    def test_label(self):
        tree = ast.parse(textwrap.dedent("""
            ::foo::
            """))
        exp = Chunk(body=Block(body=[
            Label(id=Name('foo'))
        ]))
        self.assertEqual(exp, tree)

        # test tokens
        nodes = list(ast.walk(tree))

        self.assertIsInstance(nodes[2], Label)
        self.assertEqual(nodes[2].tokens[0].text, '::')
        self.assertEqual(nodes[2].tokens[1].text, 'foo')
        self.assertEqual(nodes[2].tokens[2].text, '::')

    def test_goto(self):
        tree = ast.parse(textwrap.dedent("""
            goto foo
            ::foo::
            """))
        exp = Chunk(body=Block(body=[
            Goto(label=Name('foo')),
            Label(id=Name('foo'))
        ]))
        self.assertEqual(exp, tree)

        # test tokens
        nodes = list(ast.walk(tree))

        self.assertIsInstance(nodes[2], Goto)
        self.assertEqual(nodes[2].tokens[0].text, 'goto')
        self.assertEqual(nodes[2].tokens[1].text, ' ')
        self.assertEqual(nodes[2].tokens[2].text, 'foo')

    def test_break(self):
        tree = ast.parse(textwrap.dedent("""
            break
            """))
        exp = Chunk(body=Block(body=[
            Break()
        ]))
        self.assertEqual(exp, tree)

    def test_return(self):
        tree = ast.parse(r'return nil')
        exp = Chunk(body=Block(body=[Return([
            Nil()
        ])]))
        self.assertEqual(exp, tree)

    def test_return_multiple(self):
        tree = ast.parse(r'return nil, "error", 42; ')
        exp = Chunk(body=Block(body=[Return([
            Nil(), String('error'), Number(42)
        ])]))
        self.assertEqual(exp, tree)

