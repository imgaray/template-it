import json
import os
from string import Template

ARCHITECTURE_FOLDER = "architecture"
DEFAULTS_FOLDER = "defaults"
TEMPLATES_FOLDER = "templates"

def convert_to_string(element):
	if type(element) == type(""):
		return element
	if type(element) == type([]) or type(element) == type((1,)) or type(element) == type({}):
		return "\n".join(element)
	return str(element)
	
class TemplateFile(object):	
	def __init__(self, base_template, defaults = None):
		with open(base_template) as template:
			self.string_template = ''.join(template.readlines())
			self.parameters = {}
			if defaults is not None:
				with open(defaults) as fdefaults:
					self.parameters = json.load(fdefaults)		
	
	def add_parameter(self, name, value):
		self.parameters[name] = value
		
	def save_to(self, output_filename):
		temp = Template(self.string_template)
		repl = temp.substitute(self.parameters)
		with open(output_filename, 'w') as output:
			output.write(repl)
	
class ReprClass(object):
	def __init__(self, parameters_filename, structure_template_filename, method_template_filename, attribute_template_filename):
		self.attributes = {}
		with open(parameters_filename) as data_file:    
			data = json.load(data_file)
			self.type = data["type"]
			self.namespace = data["namespace"]
			self.hierarchy = data["hierarchy"]
			self.ItemName = data["ItemName"]
			self.structure_template_filename = structure_template_filename
			self.methods = self.process_methods(data["methods"])
			self.attributes = self.process_attribtues(data["attributes"])
	
	def process_methods(self, methods):
		new_attr = {}
		with open(os.path.join(TEMPLATES_FOLDER, self.method_template_filename)) as template_method:
			str_template = '\n'.join(template_method.readlines())
			for method in methods:
				template = Template(str_template)
				methods[method]["methodName"] = method
				parameters = methods[method]["parameters"]
				methods[method]["parameters"] = ",".join([parameter + " " + parameters[parameter] for parameter in parameters])
				new_attr[method] = template.substitute(methods[method])
		return new_attr
			
			
	def get_method_template_filename(self):
		return self.method_template_filename
		
	def process_attribtues(self, attributes):
		new_attr = {}
		with open(os.path.join(TEMPLATES_FOLDER, "attribute-template.txt")) as template_attribute:
			str_template = '\n'.join(template_attribute.readlines())
			for attribute in attributes:
				template = Template(str_template)
				attributes[attribute]["attributeName"] = attribute
				new_attr[attribute] = template.substitute(attributes[attribute])
		return new_attr
	
	def get_as_parameters(self):
		params = {}		
		params["type"] = self.type
		params["namespace"] = self.namespace
		params["hierarchy"] = self.hierarchy
		params["ItemName"] = self.ItemName
		params["MethodsContainer"] = "\n".join(self.methods.values())
		params["AttributesContainer"] = "\n".join(self.attributes.values())
		return params
		
	def build_from_template(self):
		template = TemplateFile(os.path.join(TEMPLATES_FOLDER, self.structure_template_filename), defaults)
		params = self.get_as_parameters()
		for parameter in parameters:
			template.add_parameter(parameter, convert_to_string(parameters[parameter]))
		template.save_to(output)

def resolve_architecture(arch_file_path):
	with open(arch_file_path) as arch_file_description:
		arch_conf = json.load(arch_file_description)
	return [ create_class_representantion(arch_conf[arch_desc]) for arch_desc in arch_conf ]
	
def create_class_representantion(description):
	return ReprClass(description["filename"], description["method_template_filename"], description["attribute_template_filename"])

def build_architecture(elements):
	for element in elements:
		element.build_from_template()
	
def main():
	build_architecture(resolve_architecture("architecture.json"))
	
if __name__ == "__main__":
	main()