<script lang="ts">
    export let data: { [key: string]: any };
</script>
<span style="
    flex-grow: {data.attr.factor ?? 1};">
    <slot />
</span>