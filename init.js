<script type="text/javascript">
      Element.prototype._attachShadow = Element.prototype.attachShadow;
      Element.prototype.attachShadow = function () {
          return this._attachShadow({ mode: "open" });
      };
</script>