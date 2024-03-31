import ShortUniqueId from "short-unique-id";

const uid = new ShortUniqueId({ length: 5 });

export function getNodeId(nodeType: string) {
  return nodeType + "-" + uid.rnd();
}

export function classNames(...classes: Array<string>): string {
  return classes.filter(Boolean).join(" ");
}
