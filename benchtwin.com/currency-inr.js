/* Display-only INR currency layer. Source catalog prices remain in USD so they stay comparable and maintainable. */
(function () {
  "use strict";

  const settings = window.BUILD2REAL_CURRENCY || { code: "INR", usdToInr: 95.1623 };
  const formatter = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: settings.code,
    currencyDisplay: "symbol",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  });

  const asInr = (usd) => formatter.format((Number(usd) || 0) * settings.usdToInr);
  window.__btMoney = asInr;

  const excluded = "script,style,textarea,code,pre,select,option,input,[contenteditable='true'],.cm-content,.editor";
  const usdAmount = /\$(\d[\d,]*(?:\.\d{1,2})?)/g;
  const convertText = (node) => {
    if (!node || !node.nodeValue || !node.nodeValue.includes("$")) return;
    const parent = node.parentElement;
    if (!parent || parent.closest(excluded)) return;
    const converted = node.nodeValue.replace(usdAmount, (_, amount) => asInr(Number(amount.replace(/,/g, ""))));
    if (converted !== node.nodeValue) node.nodeValue = converted;
  };
  const scan = (root) => {
    if (!root) return;
    if (root.nodeType === Node.TEXT_NODE) return convertText(root);
    if (root.nodeType !== Node.ELEMENT_NODE && root.nodeType !== Node.DOCUMENT_FRAGMENT_NODE) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) convertText(node);
  };

  scan(document.body);
  new MutationObserver((changes) => {
    for (const change of changes) {
      if (change.type === "characterData") convertText(change.target);
      else for (const node of change.addedNodes) scan(node);
    }
  }).observe(document.body, { childList: true, subtree: true, characterData: true });
})();
