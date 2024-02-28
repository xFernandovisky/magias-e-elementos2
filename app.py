from flask import Flask, render_template, request, redirect, url_for, session
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Definindo o nome do arquivo JSON para armazenar os dados das magias e personagens
SPELLS_JSON_FILE = 'spells.json'
CHARACTERS_JSON_FILE = 'characters.json'

# Definindo variáveis globais para armazenar magias e personagens
spells = []  # Lista de magias criadas
elements = ["Arcano", "Fogo", "Terra", "Água", "Vento", "Luz", "Natureza", "Trevas", "Tempo", "Marcial", "Necromancia", "Invocação", "Sangue", "Espaço"]
cycles = ["Truques", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]  # Lista de ciclos de magia
characters = []  # Lista de personagens criados

# Credenciais do desenvolvedor
developer_username = 'Fernandovisky'
developer_password = '0960'

class Spell:
    def __init__(self, name, description, prereq, cast_time, spell_type, spell_range, components, duration, element, cycle):
        self.name = name
        self.description = description
        self.prereq = prereq
        self.cast_time = cast_time
        self.spell_type = spell_type
        self.spell_range = spell_range
        self.components = components
        self.duration = duration
        self.element = element
        self.cycle = cycle
        self.id = None  # Adicionando um atributo 'id'

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'prereq': self.prereq,
            'cast_time': self.cast_time,
            'spell_type': self.spell_type,
            'spell_range': self.spell_range,
            'components': self.components,
            'duration': self.duration,
            'element': self.element,
            'cycle': self.cycle,
            'id': self.id
        }

class Character:
    def __init__(self, name, race, elements, spells=None):
        self.name = name
        self.race = race
        self.elements = elements
        self.spells = spells if spells is not None else []

    def add_spell(self, spell):
        self.spells.append(spell)

    def to_dict(self):
        return {
            'name': self.name,
            'race': self.race,
            'elements': self.elements,
            'spells': [spell.to_dict() for spell in self.spells]
        }

# Função para carregar os dados das magias do arquivo JSON
def load_data_from_json(json_file):
    if Path(json_file).is_file():
        with open(json_file, 'r') as f:
            return json.load(f)
    else:
        return []

# Função para salvar os dados das magias e personagens no arquivo JSON
def save_data_to_json(data, json_file):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

# Carregar as magias ao iniciar a aplicação
spells = [Spell(**spell_data) for spell_data in load_data_from_json(SPELLS_JSON_FILE)]

# Carregar os personagens ao iniciar a aplicação
characters = [Character(**char_data) for char_data in load_data_from_json(CHARACTERS_JSON_FILE)]

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html', spells=spells, elements=elements, characters=characters, cycles=cycles)

# Rota para ver detalhes de uma magia
@app.route('/spell/<int:index>/')
def spell_detail(index):
    if 0 <= index < len(spells):
        spell = spells[index]
        is_owner = session.get('is_developer', False)
        return render_template('spell_detail.html', spell=spell, is_owner=is_owner, index=index)
    else:
        return "Magia não encontrada", 404

# Rota para ver detalhes de um personagem
@app.route('/character/<int:id>/')
def character_detail(id):
    if 0 <= id < len(characters):
        character = characters[id]
        return render_template('character_detail.html', character=character)
    else:
        return "Personagem não encontrado", 404

# Rota para criar uma nova magia
@app.route('/create_spell', methods=['POST'])
def create_spell():
    name = request.form['name']
    description = request.form['description']
    prereq = request.form['prereq']
    cast_time = request.form['cast_time']
    spell_type = request.form['spell_type']
    spell_range = request.form['range']  # Alterado de 'range_' para 'spell_range'
    components = request.form['components']
    duration = request.form['duration']
    element = request.form['element']
    cycle_name = request.form['cycle']
    cycle = cycles.index(cycle_name) if cycle_name in cycles else 1  # Se o ciclo não estiver na lista, definimos como 1
    spell = Spell(name, description, prereq, cast_time, spell_type, spell_range, components, duration, element, cycle)
    spell.id = len(spells)  # Atribuindo o ID da magia
    spells.append(spell)  # Adicionando a nova magia à lista de magias
    spells.sort(key=lambda x: x.name.lower())
    save_data_to_json([spell.to_dict() for spell in spells], SPELLS_JSON_FILE)  # Salvando as magias no arquivo JSON
    return redirect(url_for('index'))

# Rota para criar um novo personagem
@app.route('/create_character', methods=['POST'])
def create_character():
    name = request.form['character_name']
    race = request.form['race']
    elements = []
    for i in range(1, 4):
        element = request.form[f'element{i}']
        level = int(request.form[f'element{i}_level'])
        elements.append((element, level))
    # Verificando se o personagem já existe
    existing_character = next((char for char in characters if char.name == name), None)
    if existing_character:
        return "Personagem já existe", 400
    else:
        character = Character(name, race, elements)
        characters.append(character)  # Adicionando o novo personagem à lista de personagens
        save_data_to_json([char.to_dict() for char in characters], CHARACTERS_JSON_FILE)  # Salvando os personagens no arquivo JSON
        return redirect(url_for('index'))

# Rota para editar um personagem
@app.route('/edit_character/<int:id>', methods=['POST'])
def edit_character(id):
    if request.method == 'POST':
        character_index = id
        character = characters[character_index]
        character.name = request.form['name']
        character.race = request.form['race']
        elements = []
        for i in range(1, 4):
            element = request.form[f'element{i}']
            level = int(request.form[f'element{i}_level'])
            elements.append((element, level))
        character.elements = elements
        save_data_to_json([char.to_dict() for char in characters], CHARACTERS_JSON_FILE)  # Salvando os personagens no arquivo JSON
        return redirect(url_for('index'))
    else:
        character_index = id
        character = characters[character_index]
        return render_template('edit_character.html', character=character)

# Rota para excluir um personagem
@app.route('/delete_character/<int:id>', methods=['POST'])
def delete_character(id):
    del characters[id]
    save_data_to_json([char.to_dict() for char in characters], CHARACTERS_JSON_FILE)  # Salvando os personagens no arquivo JSON
    return redirect(url_for('index'))

# Rota para atribuir uma magia a um personagem
@app.route('/assign_spell/<int:spell_id>/', methods=['GET', 'POST'])
def assign_spell(spell_id):
    if request.method == 'POST':
        character_id = int(request.form['character_id'])
        if 0 <= character_id < len(characters) and 0 <= spell_id < len(spells):
            character = characters[character_id]
            spell = spells[spell_id]
            character.add_spell(spell)
            save_data_to_json([char.to_dict() for char in characters], CHARACTERS_JSON_FILE)  # Salvando os personagens no arquivo JSON
            return redirect(url_for('index'))
    else:
        return render_template('assign_spell.html', spell_id=spell_id, characters=characters)

# Rota para pesquisar magias
@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    filtered_spells = [spell for spell in spells if query in spell.name.lower()]
    return render_template('index.html', spells=filtered_spells, elements=elements, characters=characters, cycles=cycles)

# Rota para filtrar magias
@app.route('/filter')
def filter():
    element = request.args.get('element', '')
    spell_type = request.args.get('type', '')

    filtered_spells = spells
    if element:
        filtered_spells = [spell for spell in filtered_spells if spell.element == element]
    if spell_type:
        filtered_spells = [spell for spell in filtered_spells if spell.spell_type == spell_type]

    return render_template('index.html', spells=filtered_spells, elements=elements, characters=characters, cycles=cycles)

# Rota para editar uma magia
@app.route('/edit_spell/<int:id>', methods=['GET', 'POST'])
def edit_spell(id):
    if request.method == 'POST':
        spell_index = id  # Usamos o índice da magia na lista
        spell = spells[spell_index]
        spell.name = request.form['name']
        spell.description = request.form['description']
        spell.prereq = request.form['prereq']
        spell.cast_time = request.form['cast_time']
        spell.spell_type = request.form['spell_type']
        spell.spell_range = request.form['range']  # Alterado de 'range_' para 'spell_range'
        spell.components = request.form['components']
        spell.duration = request.form['duration']
        spell.element = request.form['element']
        cycle_name = request.form['cycle']
        spell.cycle = cycles.index(cycle_name) if cycle_name in cycles else 1
        save_data_to_json([spell.to_dict() for spell in spells], SPELLS_JSON_FILE)  # Salvando as magias no arquivo JSON
        return redirect(url_for('spell_detail', index=spell_index))
    else:
        spell_index = id  # Usamos o índice da magia na lista
        spell = spells[spell_index]
        return render_template('edit_spell.html', spell=spell)

# Rota para excluir uma magia
@app.route('/delete_spell/<int:id>', methods=['POST'])
def delete_spell(id):
    del spells[id]
    save_data_to_json([spell.to_dict() for spell in spells], SPELLS_JSON_FILE)  # Salvando as magias no arquivo JSON
    return redirect(url_for('index'))

# Rota para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == developer_username and password == developer_password:
            session['is_developer'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

# Rota para logout
@app.route('/logout')
def logout():
    session.pop('is_developer', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
