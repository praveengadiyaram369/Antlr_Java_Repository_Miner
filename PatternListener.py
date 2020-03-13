from antlr4_package.JavaParserListener import *
from antlr4 import *
import settings


class PatternListener(JavaParserListener):
    """[this child class PatternListener is used to process all classes and methods which are related to either visitor or listener pattern]

    Arguments:
        JavaParserListener {[class]} -- [JavaParserListener is a parent class created by antlr4 and being inherited here]
    """

    # Enter a parse tree produced by JavaParser#methodDeclaration.
    def enterMethodDeclaration(self, ctx):
        """[this method is used to process all the method declarations in the repository]

        Arguments:
            ctx {[type]} -- [overriding method gives the object of the parse tree node i.e., JavaParser.MethodDeclarationContext]
        """

        if settings.is_antlr_file is True:
            method_name = ctx.IDENTIFIER().getText()
            if method_name not in ['enterRule', 'exitRule', 'visitRule']:
                if method_name.startswith('enter'):
                    settings.enter_cnt += 1
                elif method_name.startswith('exit'):
                    settings.exit_cnt += 1
                elif method_name.startswith('visit'):
                    settings.visit_cnt += 1
                            

    # Enter a parse tree produced by JavaParser#classDeclaration.
    def enterClassDeclaration(self, ctx):
        """[this method is used to process all the class declarations in the repository]

        Arguments:
            ctx {[object]} -- [overriding method gives the object of the parse tree node i.e., JavaParser.ClassDeclarationContext]
        """

        if ctx.typeType() is not None:
            extended_class_name = ctx.typeType().getText()

            # _considering only the child classes which are inheriting either a Base visitor or listener
            if 'BaseListener' in extended_class_name or 'BaseVisitor' in extended_class_name:
                settings.is_antlr_file = True
