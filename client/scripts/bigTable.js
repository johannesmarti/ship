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

  categoryOfOrder(order) {
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

class BigTableViewModel {
  constructor(schema, rowHierarchy, columnHierarchy) {
    this._schema = schema
    // Hierarchies are arrays of orders in the schema. It is assumed that
    // all elements in the arrays are distinct, that the two arrays are
    // disjoint and that together they include all orders in the schema. It
    // is also assumed that they are not empty.
    this._rowHierarchy = rowHierarchy;
    this._columnHierarchy = columnHierarchy;
  }
}

class BigTable {
  constructor(data) {
    const rawData = data.raw_data;
    const schema = new Schema(data.schema);

    this._model = new BigTableModel(schema, rawData);
    const rowHierarchy = [0, 2];
    const columnHierarchy = [1];
    this._viewModel = new BigTableViewModel(schema, rowHierarchy,
      columnHierarchy);
  }

  render() {
    let tbody;
    const table = h("table", tbody = h("tbody"));

    const upperColumnCategory = this._model._schema.categoryOfOrder(0);
    const columnCategory = this._model._schema.categoryOfOrder(1);
    const rowCategory = this._model._schema.categoryOfOrder(2);

    const upperHeadRow = h("tr", h("th"));
    const headRow = h("tr", h("th"));

    for (const upperColumnIndex of upperColumnCategory.indices()) {
      const bigCell = h("th", upperColumnCategory.nameOfIndex(upperColumnIndex));
      bigCell.colSpan = columnCategory.numIndices();
      //bigCell.setAttribute("colspan", "3");
      upperHeadRow.append(bigCell);
      for (const columnIndex of columnCategory.indices()) {
        headRow.append(h("th", columnCategory.nameOfIndex(columnIndex)));
      }
    }
    tbody.append(upperHeadRow);
    tbody.append(headRow);

    for (const rowIndex of rowCategory.indices()) {
      const row = h("tr", h("th", rowCategory.nameOfIndex(rowIndex)));
      for (const upperColumnIndex of upperColumnCategory.indices()) {
        for (const columnIndex of columnCategory.indices()) {
          const value = this._model.lookup([upperColumnIndex,columnIndex,rowIndex]);
          row.append(h("td", value.toFixed(2)));
        }
      }
      tbody.append(row)
    }
    return table;
  }
}

//function createBigTable(schema, lookup) {

function h(tagName, ...args) {
  const el = document.createElement(tagName);
  el.append(...args);
  return el;
}

console.log("bigTable loaded");

