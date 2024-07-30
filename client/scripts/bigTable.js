console.log("bigTable starts loading");

class Category {
  constructor(name, indexNameList) {
    this._name = name;
    this._indexNameList = indexNameList;
    console.assert(this._indexNameList.length >= 1,
      `Need at least one index in category ${this._name}`);
  }

  numIndices() {
    return this._indexNameList.length;
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._name;
  }

  nameOfIndex(index) {
    console.assert(this.isIndex(index),
      `${index} is not an index in category ${this.name()}`);
    return this._indexNameList[index];
  }

  indexOfName(name) {
    return this._IndexNameList.indexOf(name);
  }
}

function categoryFromJSON(spec) {
  return new Category(spec.name, spec.indices);
}

class IdentityCategoryView {
  constructor(baseCategory) {
    this._baseCategory = baseCategory;
  }

  numIndices() {
    return this._baseCategory.numIndices();
  }

  name() {
    return this._baseCategory.name();
  }

  nameOfIndex(index) {
    return this._baseCategory.nameOfIndex(index);
  }

  transform(index) {
    return index;
  }
}

class FixedValueCategoryView {
  constructor(baseCategory, fixedIndex) {
    this._baseCategory = baseCategory;
    this._fixedIndex = fixedIndex;
  }

  nameOfFixedIndex() {
    return this._baseCategory.nameOfIndex(this._fixedIndex);
  }

  numIndices() {
    return 1;
  }

  name() {
    return this._baseCategory.name() + `[{this.nameOfFixedIndex()}]`;
  }

  nameOfIndex(index) {
    console.assert(index === 0,
      `${index} is not a index in the fixed categroy ${this.name()} because it is not equal to 0`);
    return nameOfFixedIndex(); 
  }

  transform(index) {
    return this._fixedIndex;
  }
}

class RemappingCategoryView {
  constructor(baseCategory, remapper, name) {
    this._baseCategory = baseCategory;
    this._remapper = remapper;
    this._name = name;
  }

  numIndices() {
    return this._remapper.length;
  }

  name() {
    return this._name;
  }

  nameOfIndex(index) {
    return this._baseCategory.nameOfIndex(this.transform(index)); 
  }

  transform(index) {
    console.assert(0 <= index && index < this.numIndices(),
      `${index} is not a index in the remapping category ${this.name()}`);

    return this._remapper[index];
  }
}

function exponentialRemapper(baseCategory, center) {
  console.assert(0 <= center && center < baseCategory.numIndices(),
    `center point ${center} is not a index in the base category ${baseCategory.name()}`);
  // This could be computed more efficiently. I don't care.
  const remapper = [center];
  {
    let dist = 1;
    if (center !== 0) {
      while (true) {
        if (center - dist <= 0) {
          remapper.unshift(0);
          break;
        }
        remapper.unshift(center - dist);
        dist *= 2;
      }
    }
  }
  {
    let dist = 1;
    const last = baseCategory.numIndices() - 1;
    if (center !== last) {
      while (true) {
        if (center + dist >= last) {
          remapper.push(last);
          break;
        }
        remapper.push(center + dist);
        dist *= 2;
      }
    }
  }

  const name = `exponential remapper on {baseCategory.name()} around
{baseCategory.nameOfIndex(center)}`;
  return new RemappingCategoryView(baseCategory, remapper, name);
}

class Schema {
  constructor(categories) {
    this._categories = categories;
  }

  isOrder(number) {
    return 0 <= number && number < this.numCategories();
  }

  *orders() {
    for (let order = 0; order < this.numCategories(); order++) {
      yield order;
    }
  }

  numCategories() {
    return this._categories.length;
  }

  categoryAtOrder(order) {
    console.assert(this.isOrder(order), `${order} is not an order in schema`);
    return this._categories[order];
  }

  orderOfCategoryName(categoryName) {
    return this._categories.findIndex((c) => c.name() === categoryName);
  }

  categoryOfName(categoryName) {
    return this.categoryAtOrder(this.orderOfCategoryName(categoryName));
  }
}

function schemaFromJSON(spec) {
  return new Schema(spec.map((spec) => categoryFromJSON(spec)));
}

function virtualize(schema, transformer) {
  const array = schema._categories.map((c) => {
    const id = (c) => new IdentityCategoryView(c);
    const name = c.name();
    const mapper = transformer[name] || id;
    return mapper(c);
  });
  return new Schema(array);
}

function toAbsoluteIndex(schema, absoluteAddress) {
  console.assert(absoluteAddress.length === schema.numCategories(),
    `absolute address is not of the right length`);
  let multiplier = 1;
  let absoluteIndex = 0;
  for (let o = schema.numCategories() - 1; o >= 0; o--) {
      absoluteIndex += absoluteAddress[o] * multiplier;
      multiplier *= schema.categoryAtOrder(o).numIndices();
  }
  return absoluteIndex;
}

class PhysicalDataView {
  constructor(json) {
    this._schema = schemaFromJSON(json.schema);
    this._rawData = json.raw_data;
  }

  schema() {
    return this._schema;
  }

  lookup(absoluteAddress) {
    return this._rawData[toAbsoluteIndex(this._schema, absoluteAddress)];
  }
}

class VirtualDataView {
  constructor(physicalView, virtualSchema) {
    this._physicalView = physicalView;
    this._schema = virtualSchema;
  }

  schema() {
    return this._schema;
  }
  
  lookup(absoluteAddress) {
    const physicalAddress = new Array(absoluteAddress.length);
    for (let o of this.schema().orders()) {
      physicalAddress[o] = this.schema().categoryAtOrder(o).transform(absoluteAddress[o]);
    }
    return this._physicalView.lookup(physicalAddress);
  }
}

class MutableHierarchicalIterator {
  constructor(schema, hierarchy) {
    this._schema = schema;
    this._hierarchy = hierarchy;
    this._array = new Array(hierarchy.length).fill(0);
  }

  address() {
    return this._array;
  }

  increment() {
    let k = this._array.length - 1;
    do {
      const category = this._schema.categoryAtOrder(this._hierarchy[k]);
      this._array[k]++;
      if (this._array[k] !== category.numIndices()) {
        return true;
      }
      this._array[k] = 0;
      k--;
    } while (k >= 0);
    return false;
  }

  *freshDigits() {
    let k = this._array.length - 1;
    do {
      const category = this._schema.categoryAtOrder(this._hierarchy[k]);
      yield [k, this._array[k], category];
      if (this._array[k] !== 0) {
        break;
      }
      k--;
    } while (k >= 0);
  }
}

class BigTable {
  constructor(dataView) {
    this._dataView = dataView;
  }

  schema() {
    return this._dataView.schema();
  }

  checkHierarchies(rowHierarchy, columnHierarchy) {
    const rSet = new Set(rowHierarchy);
    const cSet = new Set(columnHierarchy);
    console.assert(rowHierarchy.length > 0,
      "row hierarchy is empty");
    console.assert(columnHierarchy.length > 0,
      "column hierarchy is empty");
    console.assert(rSet.size === rowHierarchy.length,
      "row hierarchy contains duplicates");
    console.assert(cSet.size === columnHierarchy.length,
      "column hierarchy contains duplicates");
    console.assert(rowHierarchy.every(item => !cSet.has(item)),
      "row and column hierarchies are not disjoint");
    for (let o = 0; o < this.schema().numCategories(); o++) {
      console.assert(rSet.has(o) || cSet.has(o),
        "some category from the schema is not in either row nor column hierarchy");
    }
    console.assert(rSet.size + cSet.size === this.schema().numCategories(),
      "row or column hierarchy contain categories that are not in the schema");
  }

  render(rowHierarchy, columnHierarchy) {
    this.checkHierarchies(rowHierarchy, columnHierarchy);

    // using arrow function to get the right behavior of 'this'
    const absoluteAddress = (rowAddress, columnAddress) => {
      console.assert(rowAddress.length === rowHierarchy.length,
        "row address length does not match the length of the row hierarchy");
      console.assert(columnAddress.length === columnHierarchy.length,
        "column address length does not match the length of the column hierarchy");
    
      const address = Array(this.schema().numCategories());
      for (const [j, index] of rowAddress.entries()) {
        address[rowHierarchy[j]] = index;
      }
      for (const [j, index] of columnAddress.entries()) {
        address[columnHierarchy[j]] = index;
      }
      return address;
    }

    let tbody;
    const table = h("table", tbody = h("tbody"));

    // draw column headings
    {
      let rowArray = new Array(columnHierarchy.length);
      for (let o = 0; o < rowArray.length; o++) {
        const row = h("tr");
        rowArray[o] = row;
        tbody.append(row);
      }
      // generate top left control cells:
      {
        const lastRow = columnHierarchy.length - 1;
        for (let k = 0; k < lastRow; k++) {
          for (let l = 0; l < rowHierarchy.length - 1; l++) {
            rowArray[k].append(h("td"));
          }
          const button = createButton("& v", () => {
            const tmp = columnHierarchy[k];
            columnHierarchy[k] = columnHierarchy[k + 1];
            columnHierarchy[k + 1] = tmp;
            table.replaceWith(this.render(rowHierarchy, columnHierarchy));
          });
          rowArray[k].append(h("td", button));
        }
        // last row of buttons on to of rowHierarchy
        for (let l = 0; l < rowHierarchy.length - 1; l++) {
          const button = createButton("& >", () => {
            const tmp = rowHierarchy[l];
            rowHierarchy[l] = rowHierarchy[l + 1];
            rowHierarchy[l + 1] = tmp;
            table.replaceWith(this.render(rowHierarchy, columnHierarchy));
          });
          rowArray[lastRow].append(h("td", button));
        }
        const lastCell = h("td");
        if (rowHierarchy.length > 1) {
          const button = createButton("^", () => {
            const switcher = rowHierarchy.pop();
            columnHierarchy.push(switcher);
            table.replaceWith(this.render(rowHierarchy, columnHierarchy));
          });
          lastCell.append(button);
        }
        {
          const button = createButton("&", () => {
            const fromRow = rowHierarchy.pop();
            const fromColumn = columnHierarchy.pop();
            rowHierarchy.push(fromColumn);
            columnHierarchy.push(fromRow);
            table.replaceWith(this.render(rowHierarchy, columnHierarchy));
          });
          lastCell.append(button);
        }
        if (columnHierarchy.length > 1) {
          const button = createButton("<", () => {
            const switcher = columnHierarchy.pop();
            rowHierarchy.push(switcher);
            table.replaceWith(this.render(rowHierarchy, columnHierarchy));
          });
          lastCell.append(button);
        }
        rowArray[lastRow].append(lastCell);
      }
      // go through all cells and draw their heading
      const columnIterator = new MutableHierarchicalIterator(this.schema(), columnHierarchy);
      do {
        const row = h("tr");
        // draw row heading
        let multiplier = 1;
        for (let [o, index, category] of columnIterator.freshDigits()) {
          const cell = h("th", category.nameOfIndex(index));
          cell.colSpan = multiplier;
          rowArray[o].append(cell);
          multiplier *= category.numIndices();
        }
      } while (columnIterator.increment());
    }


    // draw data rows with iterator
    const rowIterator = new MutableHierarchicalIterator(this.schema(), rowHierarchy);
    do {
      const row = h("tr");
      // draw row heading
      let multiplier = 1;
      for (let [o, index, category] of rowIterator.freshDigits()) {
        const cell = h("th", category.nameOfIndex(index));
        cell.rowSpan = multiplier;
        row.prepend(cell);
        multiplier *= category.numIndices();
      }
      // draw data cells
      const columnIterator = new MutableHierarchicalIterator(this.schema(), columnHierarchy);
      do {
        const address = absoluteAddress(rowIterator.address(),
                                        columnIterator.address());
        const value = this._dataView.lookup(address);
        row.append(h("td", value.toFixed(3)));
      } while(columnIterator.increment());
      tbody.append(row);
    } while (rowIterator.increment());

    return table;
  }
}

function h(tagName, ...args) {
  const el = document.createElement(tagName);
  el.append(...args);
  return el;
}

function createButton(text, onClickFunction) {
  let button = document.createElement("button");
  button.textContent = text;
  button.onclick = onClickFunction;
  return button;
}

console.log("bigTable loaded");
