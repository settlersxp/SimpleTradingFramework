<script lang="ts">
    import { page } from "$app/state";
    let { slug } = page.params;
</script>

<h1>blog post</h1>
<p>slug: {slug}</p>
