console.log("bigTable starts loading");

class Category {
  constructor(spec) {
    this._name = spec.name;
    this._nameList = spec.indices;
    console.assert(this._nameList.length >= 1,
      `Need at least one index in category ${this._name}`);
  }

  isIndex(number) {
    return 0 <= number && number < this._nameList.length;
  }

  name() {
    return this._name;
  }

  nameOfIndex(index) {
    console.assert(this.isIndex(index), `${index} is not an index in category`);
    return this._nameList[index];
  }

  indexOfName(name) {
    return this._nameList.indexOf(name);
  }

  *indices() {
    for (let index = 0; index < this._nameList.length; index++) {
      yield index;
    }
  }

  numIndices() {
    return this._nameList.length;
  }
}

class Schema {
  constructor(spec) {
    this._numCategories = spec.length;
    this._categories = spec.map((spec) => new Category(spec));
  }

  isOrder(number) {
    return 0 <= number && number < this._numCategories;
  }

  *orders() {
    for (let order = 0; order < this._numCategories; order++) {
      yield order;
    }
  }

  numCategories() {
    return this._numCategories;
  }

  categoryAtOrder(order) {
    console.assert(this.isOrder(order), `${order} is not an order in schema`);
    return this._categories[order];
  }

  orderOfCategoryName(categoryName) {
    return this._categories.findIndex((c) => c.name() === categoryName);
  }

  toAbsoluteIndex(absoluteAddress) {
    console.assert(absoluteAddress.length === this.numCategories(),
      `absolute address is not of the right length`);
    let multiplier = 1;
    let absoluteIndex = 0;
    for (let o = this.numCategories() - 1; o >= 0; o--) {
        absoluteIndex += absoluteAddress[o] * multiplier;
        multiplier *= this._categories[o].numIndices();
    }
    return absoluteIndex;
  }
}

class BigTableModel {
  constructor(schema, rawData) {
    this._schema = schema;
    this._rawData = rawData;
  }

  lookup(absoluteAddress) {
    return this._rawData[this._schema.toAbsoluteIndex(absoluteAddress)];
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
  constructor(data) {
    const rawData = data.raw_data;
    const schema = new Schema(data.schema);

    this._model = new BigTableModel(schema, rawData);
    this._schema = schema;
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
    for (let o = 0; o < this._schema.numCategories(); o++) {
      console.assert(rSet.has(o) || cSet.has(o),
        "some category from the schema is not in either row nor column hierarchy");
    }
    console.assert(rSet.size + cSet.size === this._schema.numCategories(),
      "row or column hierarchy contain categories that are not in the schema");
  }

  dynamicRender(rowHierarchy, columnHierarchy) {
    this.checkHierarchies(rowHierarchy, columnHierarchy);

    // using arrow function to get the right behavior of this
    const absoluteAddress = (rowAddress, columnAddress) => {
      console.assert(rowAddress.length === rowHierarchy.length,
        "row address length does not match the length of the row hierarchy");
      console.assert(columnAddress.length === columnHierarchy.length,
        "column address length does not match the length of the column hierarchy");
    
      const address = Array(this._schema.numCategories());
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
      // generate top left cell:
      {
        const cell = h("td")
        cell.colSpan = rowHierarchy.length;
        cell.rowSpan = columnHierarchy.length;
        rowArray[0].append(cell);
      }
      // go through all cells and draw their heading
      const columnIterator = new MutableHierarchicalIterator(this._schema, columnHierarchy);
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
    const rowIterator = new MutableHierarchicalIterator(this._schema, rowHierarchy);
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
      const columnIterator = new MutableHierarchicalIterator(this._schema, columnHierarchy);
      do {
        const address = absoluteAddress(rowIterator.address(),
                                        columnIterator.address());
        const value = this._model.lookup(address);
        row.append(h("td", value.toFixed(2)));
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

console.log("bigTable loaded");
