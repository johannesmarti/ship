import { Schema } from './schema.mjs';
import { Position, Arrangement } from './arrangement.mjs';

export function h(tagName, ...args) {
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

class IdentityDimensionTransformer {
  constructor(baseDimension) {
    this._baseDimension = baseDimension;
  }

  numIndices() {
    return this._baseDimension.numIndices();
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._baseDimension.name();
  }

  nameOfIndex(index) {
    return this._baseDimension.nameOfIndex(index);
  }

  transform(index) {
    return index;
  }
}

class FixedValueDimensionTransformer {
  constructor(baseDimension, fixedIndex) {
    this._baseDimension = baseDimension;
    this._fixedIndex = fixedIndex;
  }

  nameOfFixedIndex() {
    return this._baseDimension.nameOfIndex(this._fixedIndex);
  }

  numIndices() {
    return 1;
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._baseDimension.name() + `[${this.nameOfFixedIndex()}]`;
  }

  nameOfIndex(index) {
    console.assert(index === 0,
      `${index} is not a index in the fixed dimension ${this.name()} because it is not equal to 0`);
    return this.nameOfFixedIndex(); 
  }

  transform(index) {
    return this._fixedIndex;
  }
}

class RemappingDimensionTransformer {
  constructor(baseDimension, remapper, name) {
    this._baseDimension = baseDimension;
    this._remapper = remapper;
    this._name = name;
  }

  numIndices() {
    return this._remapper.length;
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._name;
  }

  nameOfIndex(index) {
    return this._baseDimension.nameOfIndex(this.transform(index)); 
  }

  transform(index) {
    console.assert(0 <= index && index < this.numIndices(),
      `${index} is not a index in the remapping dimension ${this.name()}`);

    return this._remapper[index];
  }
}

function exponentialRemapper(baseDimension, center) {
  console.assert(0 <= center && center < baseDimension.numIndices(),
    `center point ${center} is not a index in the base dimension ${baseDimension.name()}`);
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
    const last = baseDimension.numIndices() - 1;
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

  const name = `exponential remapper on ${baseDimension.name()} around
${baseDimension.nameOfIndex(center)}`;
  return new RemappingDimensionTransformer(baseDimension, remapper, name);
}

class TransformedDataView {
  constructor(physicalView, transformationSchema) {
    this._physicalView = physicalView;
    this._transformationSchema = transformationSchema;
  }

  schema() {
    return this._transformationSchema;
  }
  
  lookup(absoluteAddress) {
    const schema = this.schema();
    const physicalAddress = new Array(absoluteAddress.length);
    for (let o of schema.orders()) {
      physicalAddress[o] = schema.dimensionAtOrder(o).transform(absoluteAddress[o]);
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
      const dimension = this._schema.dimensionAtOrder(this._hierarchy[k]);
      this._array[k]++;
      if (this._array[k] !== dimension.numIndices()) {
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
      yield [k, this._hierarchy[k], this._array[k]];
      if (this._array[k] !== 0) {
        break;
      }
      k--;
    } while (k >= 0);
  }
}

function indexInDimensionFromJSON(dimension, json) {
  const defaultValue = 0;
  return {
    "first": 0,
    "mid": dimension.numIndices() / 2,
    "last": dimension.numIndices() - 1
  }[json] || (Number.isInteger(json) ? json : defaultValue);
}

export class Virtualizer {
  constructor(configuration) {
    this._configuration = configuration;
  }

  configuration() {
    return this._configuration;
  }

  virtualize(schema) {
    const array = schema._dimensions.map((_, o) => {
      const dimension = schema.dimensionAtOrder(o);
      const descriptor = this._configuration[o] || {"type": "id"};

      const id = () => new IdentityDimensionTransformer(dimension);
      const onFixed = () => {
            const fixedValue = indexInDimensionFromJSON(dimension, descriptor["value"]);
            return new FixedValueDimensionTransformer(dimension, fixedValue);
      };
      const mapper = {
        "id": id,
        "fixed": onFixed,
        "fixed_id": onFixed,
        "fixed_exponential": onFixed,
        "exponential": () => {
            const center = indexInDimensionFromJSON(dimension, descriptor["center"]);
            return exponentialRemapper(dimension, center);
          }
      }[descriptor["type"]] || id;
      return mapper();
    });
    return new Schema(array);
  }

  update(order, baseIndex, baseDimension) {
    const configuration = this.configuration();
    const description = configuration[order] || {"type": "id"};
    const currentType = description["type"] || "id";
    const computeNewDescription = {
      "id": () => { return {"type": "fixed_id", "value": baseIndex}; },
      "fixed": () => { return {"type": "id"}; },
      "fixed_id": () => { return {"type": "id"}; },
      "fixed_exponential": () => {
          return {"type": "exponential",
                  "center": description["value"]};
        },
      "exponential": () => {
          const center = indexInDimensionFromJSON(baseDimension,
            description["center"]);
          if (baseIndex === center) {
            return {"type": "fixed_exponential",
                    "value": description["center"]};
          } else {
            return {"type": "exponential",
                    // TODO: Here we could make an effort to
                    // reconstruct the JSON descriptors "first",
                    // "mid" and "last".
                    "center": baseIndex};
          }
        }
    }[currentType];
    const newDescription = computeNewDescription()
    const newConfiguration = { ...configuration, [order]: newDescription};
    const newVirtualizer = new Virtualizer(newConfiguration);
    return newVirtualizer;
  }
}

export class BigTable {
  constructor(dataView) {
    this._dataView = dataView;
  }

  render(arrangement, virtualizer) {
    const baseSchema = this._dataView.schema();
    // could be done in constructor, need to think how I do this stuff
    // in the interface
    const schema = virtualizer.virtualize(baseSchema);
    arrangement.checkInternally();
    arrangement.checkAgainstSchema(schema);
    const transformedDataView = new TransformedDataView(this._dataView, schema);
    arrangement.checkAgainstSchema(schema);
    const [rowHierarchy, columnHierarchy] = arrangement.hierarchies();

    let frow;
    let tbody;
    let div = h("div",
        h("table", h("tbody", frow = h("tr"))),
        h("table", tbody = h("tbody"))
    );

    for (const fixedOrder of arrangement.fixed()) {
      const order = fixedOrder.order();
      const fixedIndex = fixedOrder.fixedIndex();
      const dimension = schema.dimensionAtOrder(order);
      const cell = h("th", dimension.nameOfIndex(fixedIndex));
      frow.append(cell);
    }

    // using arrow function to get the right behavior of 'this'
    const createHeaderCell = (order, dimension, index) => {
      const cell = h("th", dimension.nameOfIndex(index));
      cell.addEventListener('click', () => {
        const baseDimension = baseSchema.dimensionAtOrder(order);
        const baseIndex = dimension.transform(index);
        const newVirtualizer =
            virtualizer.update(order, baseIndex, baseDimension);
        div.replaceWith(this.render(arrangement, newVirtualizer));
      });
      return cell;
    }
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
            const fromPosition = Position.column(k);
            const toPosition = Position.column(k + 2);
            const newArrangement = arrangement.move(fromPosition, toPosition, -1);
            div.replaceWith(this.render(newArrangement, virtualizer));
          });
          rowArray[k].append(h("td", button));
        }
        // last row of buttons on to of rowHierarchy
        for (let l = 0; l < rowHierarchy.length - 1; l++) {
          const button = createButton("& >", () => {
            const fromPosition = Position.row(l);
            const toPosition = Position.row(l + 2);
            const newArrangement = arrangement.move(fromPosition, toPosition, -1);
            div.replaceWith(this.render(newArrangement, virtualizer));
          });
          rowArray[lastRow].append(h("td", button));
        }
        const lastCell = h("td");
        if (rowHierarchy.length > 1) {
          const button = createButton("^", () => {
            const fromPosition = Position.row(rowHierarchy.length - 1);
            const toPosition = Position.column(columnHierarchy.length);
            const newArrangement = arrangement.move(fromPosition, toPosition, -1);
            div.replaceWith(this.render(newArrangement, virtualizer));
          });
          lastCell.append(button);
        }
        {
          const button = createButton("&", () => {
            const fromPosition1 = Position.row(rowHierarchy.length - 1);
            const toPosition1 = Position.column(columnHierarchy.length);
            const newArrangement = arrangement.move(fromPosition1, toPosition1, -1);
            const fromPosition2 = Position.column(columnHierarchy.length - 1);
            const toPosition2 = Position.row(rowHierarchy.length - 1);
            const newerArrangement = newArrangement.move(fromPosition2, toPosition2, -1);
            div.replaceWith(this.render(newerArrangement, virtualizer));
          });
          lastCell.append(button);
        }
        if (columnHierarchy.length > 1) {
          const button = createButton("<", () => {
            const fromPosition = Position.column(columnHierarchy.length - 1);
            const toPosition = Position.row(rowHierarchy.length);
            const newArrangement = arrangement.move(fromPosition, toPosition, -1);
            div.replaceWith(this.render(newArrangement, virtualizer));
          });
          lastCell.append(button);
        }
        rowArray[lastRow].append(lastCell);
      }
      // go through all cells and draw their heading
      const columnIterator = new MutableHierarchicalIterator(schema, columnHierarchy);
      do {
        const row = h("tr");
        // draw row heading
        let multiplier = 1;
        for (let [k, order, index] of columnIterator.freshDigits()) {
          const dimension = schema.dimensionAtOrder(order);
          const cell = createHeaderCell(order, dimension, index);
          cell.colSpan = multiplier;
          rowArray[k].append(cell);
          multiplier *= dimension.numIndices();
        }
      } while (columnIterator.increment());
    }

    // draw data rows with iterator
    const rowIterator = new MutableHierarchicalIterator(schema, rowHierarchy);
    do {
      const row = h("tr");
      // draw row heading
      let multiplier = 1;
      for (let [k, order, index] of rowIterator.freshDigits()) {
        const dimension = schema.dimensionAtOrder(order);
        const cell = createHeaderCell(order, dimension, index);
        cell.rowSpan = multiplier;
        row.prepend(cell);
        multiplier *= dimension.numIndices();
      }
      // draw data cell
      const columnIterator = new MutableHierarchicalIterator(schema, columnHierarchy);
      do {
        const address = arrangement.absoluteAddress(rowIterator.address(),
                                                    columnIterator.address());
        const value = transformedDataView.lookup(address);
        row.append(h("td", value.toFixed(3)));
      } while(columnIterator.increment());
      tbody.append(row);
    } while (rowIterator.increment());
    return div;
  }
}
