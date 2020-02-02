from antlr4_package.JavaParser import *
from antlr4_package.JavaParserVisitor import *

class JavaCodeParser(JavaParserVisitor):

    # Visit a parse tree produced by JavaParser#compilationUnit.
    def visitCompilationUnit(self, ctx:JavaParser.CompilationUnitContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaParser#packageDeclaration.
    def visitPackageDeclaration(self, ctx:JavaParser.PackageDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaParser#importDeclaration.
    def visitImportDeclaration(self, ctx:JavaParser.ImportDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaParser#classDeclaration.
    def visitClassDeclaration(self, ctx:JavaParser.ClassDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaParser#methodDeclaration.
    def visitMethodDeclaration(self, ctx:JavaParser.MethodDeclarationContext):
        return self.visitChildren(ctx)